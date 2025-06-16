from image_validator import ImageValidator
if __name__ == "__main__":
    agent = ImageValidator(threshold=0.3)

    task = {
        "image_path": "../assets/panel1.png",
        "caption_parts": {
            "scene": "the scene is a green jungle with lots of trees ,flowers and the ground has green grass with sun shining throught the trees ",
            "character": "two hedgehogs",
            "action": "coming towards each other ",
            "emotion": "trwo happy hedgehogs"
        },
        "style_prompt": "new style cartoons image",

        # Optional custom weights
        "weights": {
            "scene": 0.25,
            "character": 0.25,
            "action": 0.2,
            "emotion": 0.1,
            "style": 0.1,
        },

        # Optional custom thresholds
        "thresholds": {
            "scene": 0.25,
            "character": 0.3,
            "action": 0.3,
            "emotion": 0.2,
            "style": 0.3,
        }
    }

    result = agent.run(task)

    print("\n--- CLIP Validation Report ---")
    for key, value in result.items():
        print(f"{key}: {value}")
