from agnets.blip_captioner import blip_caption_folder

# Caption all images in the output folder (change path as needed)
captions = blip_caption_folder("output/panels")  # or "output/" if that's your image dir
print(captions)

# Now you can use `captions` for BERT score validation