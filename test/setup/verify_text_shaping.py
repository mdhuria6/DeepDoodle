from PIL import Image, ImageDraw, ImageFont, features

# Check if Raqm (libraqm) support is available
raqm_available = features.check("raqm")
print(f"Pillow version: {Image.__version__}")
print(f"RAQM (libraqm) support available: {raqm_available}")

if not raqm_available:
    print("RAQM support is NOT available. Text shaping may not work correctly for complex scripts.")
    print("Please ensure libraqm is installed and Pillow was compiled with it.")
    # You might want to exit or handle this case appropriately
    # exit()
else:
    print("RAQM support is available.")

# Define image size and background color
width, height = 400, 200
background_color = (255, 255, 255)  # White

# Create a new image with a white background
image = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(image)

# Text to render (Hindi example: "Hello World")
text_to_render = "नमस्ते दुनिया"
text_color = (0, 0, 0)  # Black

# Attempt to load a font
# Using the Roboto font from your assets directory.
# For complex scripts, a font that supports those scripts is crucial.
# Roboto might have limited support for Devanagari, a dedicated Devanagari font would be better for thorough testing.
# Attempt to use a common system font first, then guide user if it fails.
font_name_primary = "assets/fonts/NotoSansDevanagari/NotoSansDevanagari-VariableFont_wdth,wght.ttf" # A good font for Devanagari
font_name_secondary_suggestion = "Arial.ttf" # Fallback, may not have full Devanagari support
font_path = font_name_primary
font_size = 40

try:
    font = ImageFont.truetype(font_path, font_size)
    print(f"Successfully loaded font: {font_path}")
except IOError:
    print(f"Could not load font: '{font_path}'. Trying secondary suggestion: '{font_name_secondary_suggestion}'")
    try:
        font_path = font_name_secondary_suggestion
        font = ImageFont.truetype(font_path, font_size)
        print(f"Successfully loaded font: {font_path}")
    except IOError:
        print(f"Could not load font: '{font_path}'.")
        print(f"This usually means the font is not installed or the path is incorrect.")
        print(f"For Hindi (Devanagari), please ensure you are using a font with Devanagari glyphs.")
        print(f"Consider installing a font like 'Noto Sans Devanagari' and updating the 'font_path' variable in this script.")
        print(f"You can download Noto Sans Devanagari from: https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari")
        print(f"Attempting to use default font as a last resort (may not support Devanagari).")
        try:
            font = ImageFont.load_default() # Default font might not support Devanagari well
            print("Loaded default font.")
        except IOError:
            print("Could not load default font. Text rendering will likely fail.")
            font = None # type: ignore
except ImportError:
    print("ImportError related to font loading, ensure Pillow is correctly installed with Freetype support.")
    font = None # type: ignore


if font:
    # Calculate text position (centered)
    # The textbbox method with RAQM should give accurate bounding box for shaped text
    try:
        # For Pillow versions that support anchor and language in text()
        # Older versions might require text_align and manual positioning based on textsize()
        # Pillow 10+ uses textlength for width, and textbbox for full bounding box
        bbox = draw.textbbox((0, 0), text_to_render, font=font, language="hi")
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) / 2
        y = (height - text_height) / 2 - bbox[1] # Adjust y by the top of the bounding box

        # Draw the text
        # Specifying the language is good practice if the font/Pillow supports it for shaping
        draw.text((x, y), text_to_render, font=font, fill=text_color, language="hi")
        print(f"Text drawn: '{text_to_render}'")
    except Exception as e:
        print(f"Error during text drawing: {e}")
        print("Attempting to draw with basic_layout as fallback if RAQM specific call failed.")
        try:
            # Fallback for older Pillow or if specific RAQM features cause issues
            # This might not render complex scripts correctly if RAQM is not used implicitly
            text_width_fallback, text_height_fallback = draw.textsize(text_to_render, font=font)
            x_fallback = (width - text_width_fallback) / 2
            y_fallback = (height - text_height_fallback) / 2
            draw.text((x_fallback, y_fallback), text_to_render, font=font, fill=text_color)
            print(f"Text drawn with fallback: '{text_to_render}'")
        except Exception as e_fallback:
            print(f"Error during fallback text drawing: {e_fallback}")


    # Save the image
    output_image_path = "test/setup/text_shaping_verification.png"
    try:
        image.save(output_image_path)
        print(f"Image saved to {output_image_path}")
        print("Please open the image to visually verify the text shaping.")
    except Exception as e:
        print(f"Error saving image: {e}")
else:
    print("Font not loaded, cannot render text.")

print("\nScript finished.")
