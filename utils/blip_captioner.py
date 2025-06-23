import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load BLIP model and processor once (singleton pattern)
_processor = None
_model = None

def get_blip_model():
    global _processor, _model
    if _processor is None or _model is None:
        _processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        _model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    return _processor, _model

def blip_caption_image(image_path: str, prompt: str = None) -> str:
    """
    Generates a caption for the given image using BLIP.
    If prompt is provided, uses conditional captioning; else, unconditional.
    """
    processor, model = get_blip_model()
    raw_image = Image.open(image_path).convert('RGB')
    if prompt:
        inputs = processor(raw_image, prompt, return_tensors="pt")
    else:
        inputs = processor(raw_image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def blip_caption_folder(folder_path: str, prompt: str = None) -> dict:
    """
    Captions all images in a folder. Returns a dict {filename: caption}.
    """
    captions = {}
    for fname in os.listdir(folder_path):
        if fname.lower().endswith(('.png', '.jpg')):
            img_path = os.path.join(folder_path, fname)
            try:
                caption = blip_caption_image(img_path, prompt)
                captions[fname] = caption
                print(f"{fname}: {caption}")
            except Exception as e:
                print(f"Error processing {fname}: {e}")
    return captions