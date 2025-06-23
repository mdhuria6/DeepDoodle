from transformers import CLIPProcessor, CLIPModel
from PIL import Image, UnidentifiedImageError
import torch
import torch.nn.functional as F
from models.comic_generation_state import ComicGenerationState
from utils.llm_factory import get_model_client


class ImageValidator:
    def __init__(self, model_name="openai/clip-vit-large-patch14", threshold=0.225, device=None):
        # Automatically choose the best available device: MPS (Mac), CUDA (GPU), or CPU
        self.device = device or (
            "mps" if torch.backends.mps.is_available()
            else "cuda" if torch.cuda.is_available()
            else "cpu"
        )
        print(f"[VALIDATOR AGENT INIT] Loading CLIP model on {self.device}")

        # Initialize a fast LLM client for summarizing long prompts
        try:
            print("[VALIDATOR AGENT INIT] Initializing summarizer LLM...")
            self.summarizer_llm = get_model_client("text", "gemini_1.5_flash")
        except Exception as e:
            print(f"  - WARNING: Could not initialize summarizer LLM: {e}")
            print("  - INFO: Summarization is DISABLED. Long prompts will be truncated.")
            self.summarizer_llm = None

        # Load the CLIP model and processor
        try:
            self.device = "cpu" # Force CPU if you keep getting meta tensor errors
            self.model = CLIPModel.from_pretrained(model_name, torch_dtype=torch.float32)
            self.processor = CLIPProcessor.from_pretrained(model_name, use_fast=True)
            self.threshold = threshold
        except Exception as e:
            raise RuntimeError(f"VALIDATOR Failed to load model or processor: {e}")

        # Set default threshold for passing a prompt match
        self.default_threshold = threshold

    def _summarize_if_needed(self, text: str, key_for_logging: str) -> str:
        """
        Summarizes a text prompt if it exceeds the CLIP model's token limit.
        Uses a fast LLM for summarization and falls back to truncation if needed.
        """
        # If summarizer isn't available, go straight to truncation fallback.
        if not self.summarizer_llm:
            # This is the original truncation logic.
            max_length = self.processor.tokenizer.model_max_length - 2
            tokens = self.processor.tokenizer.encode(text)
            if len(tokens) > max_length:
                print(f"  - WARNING: Truncating long prompt for key '{key_for_logging}'. Original length: {len(tokens)} tokens.")
                truncated_tokens = tokens[:max_length]
                return self.processor.tokenizer.decode(truncated_tokens, skip_special_tokens=True)
            return text

        # Leave a buffer for the model's special tokens (e.g., [CLS], [SEP])
        max_length = self.processor.tokenizer.model_max_length - 2
        tokens = self.processor.tokenizer.encode(text)

        if len(tokens) <= max_length:
            return text  # No summarization needed

        print(f"  - INFO: Prompt for key '{key_for_logging}' is too long ({len(tokens)} tokens). Summarizing...")

        # Use a fast LLM to summarize the text
        summarization_prompt = (
            "Summarize the following description for an AI image validation model. "
            "Focus only on the most critical visual elements, characters, and actions. "
            f"The summary must be very concise, ideally under {max_length - 10} tokens. "
            "Do not add any preamble. Just provide the summary. "
            f"Original description: \"{text}\""
        )

        try:
            summary = self.summarizer_llm.generate_text(summarization_prompt)
            summary = summary.strip().strip('"')  # Clean up LLM output

            # Check length of summary and truncate if it's still too long
            summary_tokens = self.processor.tokenizer.encode(summary)
            if len(summary_tokens) > max_length:
                print(f"  - WARNING: Summarized prompt for '{key_for_logging}' is still too long. Truncating summary.")
                truncated_tokens = summary_tokens[:max_length]
                summary = self.processor.tokenizer.decode(truncated_tokens, skip_special_tokens=True)
            
            print(f"  - INFO: Summarized prompt for '{key_for_logging}': \"{summary}\"")
            return summary

        except Exception as e:
            print(f"  - WARNING: Summarization failed for key '{key_for_logging}': {e}. Falling back to simple truncation.")
            # Fallback to simple truncation if the summarizer LLM fails
            truncated_tokens = tokens[:max_length]
            return self.processor.tokenizer.decode(truncated_tokens, skip_special_tokens=True)

    def _compute_cosine_similarities(self, image, prompts):
        # Prepare image and text data for the model
        try:
            # Process text and images separately to avoid potential processor bugs.
            # This is more robust than calling the processor on both simultaneously.
            text_inputs = self.processor.tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.processor.tokenizer.model_max_length
            )
            image_inputs = self.processor.image_processor(
                images=[image] * len(prompts),
                return_tensors="pt"
            )

            # Combine the processed inputs and move to the correct device
            inputs = {
                "input_ids": text_inputs["input_ids"].to(self.device),
                "attention_mask": text_inputs["attention_mask"].to(self.device),
                "pixel_values": image_inputs["pixel_values"].to(self.device)
            }

        except Exception as e:
            raise ValueError(f"VALIDATOR Failed to preprocess inputs: {e}")

        # Compute cosine similarities between image and text features
        try:
            with torch.no_grad():
                image_features = self.model.get_image_features(pixel_values=inputs["pixel_values"])
                text_features = self.model.get_text_features(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"]
                )

                # Normalize vectors to unit length
                image_features = F.normalize(image_features, p=2, dim=-1)
                text_features = F.normalize(text_features, p=2, dim=-1)

                # Calculate cosine similarities
                similarities = (image_features * text_features).sum(dim=-1)
                return similarities.tolist()
        except Exception as e:
            raise RuntimeError(f"VALIDATOR Failed to compute similarities: {e}")

    def run(self, task):
        print(f"[AGENT RUN] Validating image: {task['image_path']}")

        # Step 1: Load the image
        try:
            image = Image.open(task["image_path"]).convert("RGB")
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {task['image_path']}")
        except UnidentifiedImageError:
            raise ValueError(f"Unrecognized image format: {task['image_path']}")
        except Exception as e:
            raise RuntimeError(f"Error loading image: {e}")

        prompts = []  # list to hold all text prompts
        prompt_keys = []  # keep track of what each prompt corresponds to

        # Step 2: Extract, summarize if needed, and collect prompts
        caption_parts = task.get("caption_parts", {})
        if not isinstance(caption_parts, dict):
            raise ValueError("caption_parts must be a dictionary")

        for key, phrase in caption_parts.items():
            if phrase:
                summarized_phrase = self._summarize_if_needed(phrase, key)
                prompts.append(summarized_phrase)
                prompt_keys.append(key)

        # Step 3: Add optional style prompt
        if task.get("style_prompt"):
            prompts.append(task["style_prompt"])
            prompt_keys.append("style")

        if not prompts:
            return {
                "final_score": 1.0,
                "final_decision": "PASS",
                "image": task["image_path"],
                "details": {}
            }

        # Step 4: Calculate similarity scores
        scores = self._compute_cosine_similarities(image, prompts)

        # Step 5: Normalize weights (or assign equal if not provided)
        weights = task.get("weights", {key: 1.0 / len(prompt_keys) for key in prompt_keys})
        if not isinstance(weights, dict):
            raise ValueError("weights must be a dictionary")

        total_weight = sum(weights.get(k, 0) for k in prompt_keys)
        if total_weight == 0:
            normalized_weights = {k: 1.0 / len(prompt_keys) for k in prompt_keys}
        else:
            normalized_weights = {k: weights.get(k, 0) / total_weight for k in prompt_keys}

        # Step 6: Apply thresholds for each prompt
        thresholds = task.get("thresholds", {})
        if not isinstance(thresholds, dict):
            raise ValueError("thresholds must be a dictionary")

        results = {}
        weighted_score = 0.0

        # Step 7: Evaluate each prompt
        for i, key in enumerate(prompt_keys):
            score = scores[i]
            weight = normalized_weights.get(key, 0)
            threshold = thresholds.get(key, self.default_threshold)

            # Check if the score is above threshold
            passed = score >= threshold

            weighted_score += score * weight

            # Store result for this prompt
            results[key] = {
                "prompt": prompts[i],
                "cosine_similarity": round(score, 4),
                "weight": round(weight, 3),
                "threshold": round(threshold, 3),
                "decision": "PASS" if passed else "FAIL"
            }

        # Step 8: Compile final results
        final_results = {
            "final_score": round(weighted_score, 4),
            "final_decision": "PASS" if weighted_score >= self.default_threshold else "FAIL",
            "image": task["image_path"],
            "details": results
        }
        
        print(f"[VALIDATOR AGENT] Validation complete for {task['image_path']}. Score: {final_results['final_score']}")
        return final_results


_validator_instance = None

def get_validator_instance():
    """Initializes and returns a singleton instance of the ImageValidator."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ImageValidator()
    return _validator_instance

def image_validator(state: ComicGenerationState) -> dict:
    print("\n--- AGENT: Validating panel image ---")
    
    panel_image_paths = state.get("panel_image_paths", [])
    
    # The index of the panel to validate is the last one added to the list.
    # current_panel_index points to the *next* panel, so we can't use it directly.
    validation_index = len(panel_image_paths) - 1

    if validation_index < 0:
        print("Validator: No images to validate.")
        # Return current scores without modification
        return {"validation_scores": state.get("validation_scores", [])}

    # Ensure other required state lists are long enough
    scenes = state.get("scenes", [])
    if validation_index >= len(scenes):
        print(f"Validator: Error - validation_index {validation_index} is out of sync with scenes list (len {len(scenes)}).")
        return {"validation_scores": state.get("validation_scores", [])}

    panel_image_path = panel_image_paths[validation_index]
    scene = scenes[validation_index]
    character_descriptions = state.get("character_descriptions", [])

    # --- New logic to dynamically build the validation task ---
    
    # 1. The primary visual description for the panel.
    scene_description = scene.get("description", "")
    
    # 2. Extract character description and action from captions.
    character_description_for_validation = ""
    all_caption_texts = []
    if scene.get("captions"):
        for caption in scene["captions"]:
            all_caption_texts.append(caption.get("text", ""))
            speaker = caption.get("speaker")
            # If we haven't found a character yet, check if this speaker is one.
            if speaker and speaker != "Narrator" and not character_description_for_validation:
                for char in character_descriptions:
                    if char.get("name") == speaker:
                        character_description_for_validation = char.get("description", "")
                        break  # Found the character, stop searching

    # Use the combined text from all captions to represent the "action".
    action_from_captions = " ".join(all_caption_texts)

    # 3. Construct the validation task for the ImageValidator class instance.
    task = {
        "image_path": panel_image_path,
        "caption_parts": {
            "scene": scene_description,
            "character": character_description_for_validation,
        },
        "style_prompt": state.get("artistic_style"),
        # Weights determine the importance of each part in the final score.
        "weights": {"scene": 0.25, "character": 0.3, "style": 0.15},
        # Thresholds set the minimum similarity score for a part to be considered "present".
        "thresholds": {"scene": 0.20, "character": 0.20, "style": 0.20},
    }

    try:
        validator = get_validator_instance()
        validation_result = validator.run(task)
        
        print(f"  - Validation Score: {validation_result.get('final_score', 'N/A')}")
        print(f"  - Validation Decision: {validation_result.get('final_decision', 'N/A')}")

        # Append the new score to the list in the state
        current_scores = state.get("validation_scores", [])
        current_scores.append(validation_result)
        return {"validation_scores": current_scores}

    except Exception as e:
        print(f"Validator: CRITICAL ERROR during validation run: {e}")
        # On error, append a failure message to maintain list alignment
        error_result = {
            "final_score": 0.0,
            "final_decision": "ERROR",
            "image": panel_image_path,
            "details": {"error": str(e)}
        }
        current_scores = state.get("validation_scores", [])
        current_scores.append(error_result)
        return {"validation_scores": current_scores}
