from moviepy.editor import TextClip, concatenate_videoclips
import os

# List of colors (simplified and decoded for demonstration)
colors = [
    'AliceBlue', 'AntiqueWhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 
    'BlanchedAlmond', 'Blue', 'BlueViolet', 'Brown', 'Burlywood', 'CadetBlue', 'Chartreuse', 
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan', 'DarkBlue', 'DarkCyan', 
    'DarkGoldenrod', 'DarkGray', 'DarkGreen', 'DarkGrey', 'DarkKhaki', 'DarkMagenta', 'DarkOliveGreen', 
    'DarkOrange', 'DarkOrchid', 'DarkRed', 'DarkSalmon', 'DarkSeaGreen', 'DarkSlateBlue', 'DarkSlateGray', 
    'DarkSlateGrey', 'DarkTurquoise', 'DarkViolet', 'DeepPink', 'DeepSkyBlue', 'DimGray', 'DimGrey', 
    'DodgerBlue', 'Firebrick', 'FloralWhite', 'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 
    'Goldenrod', 'Gray', 'Green', 'GreenYellow', 'Honeydew', 'HotPink', 'IndianRed', 'Indigo', 'Ivory', 
    'Khaki', 'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue', 'LightCoral', 'LightCyan', 
    'LightGoldenrodYellow', 'LightGray', 'LightGreen', 'LightGrey', 'LightPink', 'LightSalmon', 
    'LightSeaGreen', 'LightSkyBlue', 'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 
    'Lime', 'LimeGreen', 'Linen', 'Magenta', 'Maroon', 'MediumAquamarine', 'MediumBlue', 'MediumOrchid', 
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen', 'MediumTurquoise', 
    'MediumVioletRed', 'MidnightBlue', 'MintCream', 'MistyRose', 'Moccasin', 'NavajoWhite', 'Navy', 
    'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed', 'Orchid', 'PaleGoldenrod', 'PaleGreen', 
    'PaleTurquoise', 'PaleVioletRed', 'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 
    'Purple', 'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Salmon', 'SandyBrown', 'SeaGreen', 
    'Seashell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue', 'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 
    'SteelBlue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White', 'WhiteSmoke', 
    'Yellow', 'YellowGreen'
]

# Create a folder for output
output_folder = "color_samples"
os.makedirs(output_folder, exist_ok=True)

# Generate a text clip for each color
clips = []
for color in colors:
    try:
        # Generate a TextClip with the name of the color as the text and the color itself
        clip = TextClip(color, fontsize=54, color='white', stroke_color='black', bg_color=color, size=(640, 500))
        clip = clip.set_duration(2)  # Duration of each clip
        clip.write_videofile(f"{output_folder}/{color}.mp4", fps=24)  # Save as video
        clips.append(clip)  # Collect clips to make a single showcase video
    except Exception as e:
        print(f"Failed to create clip for color {color}: {e}")

# Concatenate all clips into one video (optional)
final_clip = concatenate_videoclips(clips)
final_clip.write_videofile(f"{output_folder}/all_colors.mp4", fps=24)

print("Color clips created.")
