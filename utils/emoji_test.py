import os
from PIL import Image, ImageFont
import numpy as np
from pilmoji import Pilmoji

def make_emoji_image(emoji, font_path, font_size):
    """Create an image from an emoji using a specific font."""
    # emoji = emoji[0]
    print(f"trying with {emoji}")
    emoji_font = ImageFont.truetype(font_path, font_size)
    image = Image.new("RGBA", (500, 500), (0, 0, 0, 0))  # White background for better visibility
    with Pilmoji(image) as pilmoji:
        pilmoji.text((0, 0), emoji.strip(), (0, 0, 0), emoji_font)
    return image

def main():
    output_folder = "emoji_output"
    os.makedirs(output_folder, exist_ok=True)

    # Path to the emoji font
    font_path = "/Users/paulius/Library/Fonts/NotoColorEmoji-Regular.ttf"
    font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
    emojis = ["😊", "😂", "❤️", "🤔", "💥", "🎉", "🐱🎉🐱🐱"]
    font_size = 48

    for i, emoji in enumerate(emojis):
        # Create an image from each emoji
        emoji_image = make_emoji_image(emoji, font_path, font_size)
        output_path = os.path.join(output_folder, f"apple_emoji_{i}.png")
        emoji_image.save(output_path)

    print("Emoji images created successfully.")

if __name__ == "__main__":
    print("Running emoji.py")
    main()
