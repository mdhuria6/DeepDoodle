from transformers import CLIPProcessor, CLIPModel
from PIL import Image, UnidentifiedImageError
import torch
import torch.nn.functional as F
from models.comic_generation_state import ComicGenerationState


class ImageValidator:
    def __init__(self, model_name="openai/clip-vit-large-patch14", threshold=0.225, device=None):
        # Automatically choose the best available device: MPS (Mac), CUDA (GPU), or CPU
        self.device = device or (
            "mps" if torch.backends.mps.is_available()
            else "cuda" if torch.cuda.is_available()
            else "cpu"
        )
        print(f"[VALIDATOR AGENT INIT] Loading CLIP model on {self.device}")

        # Load the CLIP model and processor
        try:
            self.device = "cpu" # Force CPU if you keep getting meta tensor errors
            self.model = CLIPModel.from_pretrained(model_name, torch_dtype=torch.float32)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.threshold = threshold
        except Exception as e:
            raise RuntimeError(f"VALIDATOR Failed to load model or processor: {e}")

        # Set default threshold for passing a prompt match
        self.default_threshold = threshold

    def _compute_cosine_similarities(self, image, prompts):
        # Prepare image and text data for the model
        try:
            inputs = self.processor(
                text=prompts,
                images=[image] * len(prompts),  # repeat image for each prompt
                return_tensors="pt",
                padding=True
            ).to(self.device)
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

        # Step 2: Extract prompts from caption parts (e.g., scene, character)
        caption_parts = task.get("caption_parts", {})
        if not isinstance(caption_parts, dict):
            raise ValueError("caption_parts must be a dictionary")

        for key, phrase in caption_parts.items():
            if phrase:
                prompts.append(phrase)
                prompt_keys.append(key)

        # Step 3: Add optional style prompt
        if task.get("style_prompt"):
            prompts.append(task["style_prompt"])
            prompt_keys.append("style")

        if not prompts:
            return {
                "final_score": 1.0,
                "final_decision": "✅ PASS",
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
                "decision": "✅ PASS" if passed else "❌ FAIL"
            }

        # Step 8: Compile final results
        final_results = {
            "final_score": round(weighted_score, 4),
            "final_decision": "✅ PASS" if weighted_score >= self.default_threshold else "❌ FAIL",
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
        print("Initializing ImageValidator for the first time.")
        _validator_instance = ImageValidator()
    return _validator_instance

def image_validator(state: ComicGenerationState) -> dict:
    print("\n--- AGENT: Validating panel image ---")
    
    panel_image_paths = state.get("panel_image_paths", [])
    
    # The index of the panel to validate is the last one added to the list.
    # current_panel_index points to the *next* panel, so we can't use it directly.
    validation_index = len(panel_image_paths) - 1

    if validation_index < 0:
        print("Warning: No images found to validate.")
        return {} # Return early if there's nothing to do.

    # Ensure other required state lists are long enough
    scenes = state.get("scenes", [])
    if validation_index >= len(scenes):
        print(f"Error: Scene not found for panel index {validation_index}.")
        return {} # Cannot proceed without scene info

    panel_image_path = panel_image_paths[validation_index]
    scene = scenes[validation_index]

    task = {
        "image_path": panel_image_path,
        "caption_parts": {
            "scene": scene.get("description"),
            "character": scene.get("character_description"),
            "action": scene.get("action_description"),
        },
        "style_prompt": state.get("artistic_style"),
        "weights": {"scene": 0.4, "character": 0.4, "action": 0.2, "style": 0.1},
        "thresholds": {"scene": 0.25, "character": 0.25, "action": 0.2}
    }

    validator = get_validator_instance()
    validation_result = validator.run(task)
    
    print(f"[VALIDATOR AGENT] Validation result for panel {validation_index + 1}: {validation_result}")
    
    # Store the validation result in the state
    validation_scores = state.get("validation_scores", [])
    validation_scores.append(validation_result)

    # The image_generator is responsible for incrementing the panel index.
    # This agent's job is only to validate and return the scores.
    return {"validation_scores": validation_scores}
