import os
from PIL import Image

from models.comic_generation_state import ComicGenerationState
from utils.layout import crop_to_fit

def panel_sizer(state: ComicGenerationState) -> dict:
    print("---AGENT: Panel Sizer---")
    
    panel_image_paths = state.get("panel_image_paths", [])
    panel_layout_details = state.get("panel_layout_details", [])

    if not panel_image_paths:
        print("Error: panel_image_paths not found in state for panel_sizer.")
        return {"sized_panel_image_paths": [], "panel_layout_details": panel_layout_details} # Pass through details
    
    if not panel_layout_details or len(panel_layout_details) != len(panel_image_paths):
        print("Error: Mismatch between panel_image_paths and panel_layout_details or details missing.")
        # Fallback or error handling: perhaps try to size to a default or skip sizing
        return {"sized_panel_image_paths": panel_image_paths, "panel_layout_details": panel_layout_details} # Return original paths

    output_dir_sized = "output/panels_sized"
    os.makedirs(output_dir_sized, exist_ok=True)
    
    sized_panel_image_paths = []
    
    for i, original_panel_path in enumerate(panel_image_paths):
        layout_detail = None
        # Find the corresponding layout detail by panel_index (which should match i if lists are aligned)
        for detail in panel_layout_details:
            if detail['panel_index'] == i:
                layout_detail = detail
                break
        
        if not layout_detail:
            print(f"Warning: No layout detail found for panel at index {i} ({original_panel_path}). Skipping sizing.")
            sized_panel_image_paths.append(original_panel_path) # Add original path, or handle error differently
            continue

        try:
            target_w = layout_detail['ideal_width']
            target_h = layout_detail['ideal_height']
            
            img = Image.open(original_panel_path)
            # crop_to_fit will scale and center-crop if aspect ratios differ.
            # Since the image_generator now aims for a close aspect ratio (target_generation_width/height),
            # this crop should be minimal or primarily a resize if aspect ratios match well.
            sized_img = crop_to_fit(img, target_w, target_h)
            
            base_name = os.path.basename(original_panel_path)
            name, ext = os.path.splitext(base_name)
            output_filename = f"{name}_sized{ext}"
            output_path_sized = os.path.join(output_dir_sized, output_filename)
            
            sized_img.save(output_path_sized)
            sized_panel_image_paths.append(output_path_sized)
            print(f"   > Sized panel {i + 1}: {original_panel_path} -> {output_path_sized} ({target_w}x{target_h})")
            
        except FileNotFoundError:
            print(f"Error: Original panel image not found at {original_panel_path}")
            # Decide how to handle: append original, skip, or error out
            sized_panel_image_paths.append(original_panel_path) # Example: append original path
        except Exception as e:
            print(f"Error processing panel {original_panel_path} in panel_sizer: {e}")
            sized_panel_image_paths.append(original_panel_path) # Example: append original path
            
    return {
        "sized_panel_image_paths": sized_panel_image_paths,
        # Pass through other relevant parts of the state if needed by subsequent agents
        # "scenes": scenes, 
        "panel_layout_details": panel_layout_details # Pass this along for page_composer
    }

