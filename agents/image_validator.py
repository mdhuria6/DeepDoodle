from transformers import CLIPProcessor, CLIPModel
from PIL import Image, UnidentifiedImageError
import torch
import torch.nn.functional as F


class ImageValidator:
    def __init__(self, model_name="openai/clip-vit-large-patch14", threshold=0.3, device=None):
        # Automatically choose the best available device: MPS (Mac), CUDA (GPU), or CPU
        self.device = device or (
            "mps" if torch.backends.mps.is_available()
            else "cuda" if torch.cuda.is_available()
            else "cpu"
        )
        print(f"[AGENT INIT] Loading CLIP model on {self.device}")

        # Load the CLIP model and processor
        try:
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load model or processor: {e}")

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
            raise ValueError(f"Failed to preprocess inputs: {e}")

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
            raise RuntimeError(f"Failed to compute similarities: {e}")

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
            raise ValueError("No prompts provided for validation")

        # Step 4: Calculate similarity scores
        scores = self._compute_cosine_similarities(image, prompts)

        # Step 5: Normalize weights (or assign equal if not provided)
        weights = task.get("weights", {key: 1.0 / len(prompt_keys) for key in prompt_keys})
        if not isinstance(weights, dict):
            raise ValueError("weights must be a dictionary")

        total_weight = sum(weights.get(k, 0) for k in prompt_keys)
        if total_weight == 0:
            raise ValueError("Total weight cannot be zero")

        normalized_weights = {k: weights.get(k, 0) / total_weight for k in prompt_keys}

        # Step 6: Apply thresholds for each prompt
        thresholds = task.get("thresholds", {})
        if not isinstance(thresholds, dict):
            raise ValueError("thresholds must be a dictionary")

        results = {}
        weighted_score = 0.0
        passed_all = True

        # Step 7: Evaluate each prompt
        for i, key in enumerate(prompt_keys):
            score = scores[i]
            weight = normalized_weights.get(key, 0)
            threshold = thresholds.get(key, self.default_threshold)

            # Check if the score is above threshold
            passed = score >= threshold
            if not passed:
                passed_all = False

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
        results["final_score"] = round(weighted_score, 4)
        results["final_decision"] = "✅ PASS" if weighted_score >= self.default_threshold else "❌ FAIL"
        results["image"] = task["image_path"]
        return results
