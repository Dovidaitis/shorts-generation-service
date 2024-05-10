from moviepy.editor import TextClip, concatenate_videoclips
import os

# List of fonts
fonts = [
    'AvantGarde-Book', 'AvantGarde-BookOblique', 'AvantGarde-Demi', 'AvantGarde-DemiOblique', 'Bookman-Demi',
    'Bookman-DemiItalic', 'Bookman-Light', 'Bookman-LightItalic', 'Courier-BoldOblique', 'fixed',
    'Helvetica-BoldOblique', 'Helvetica-Narrow', 'Helvetica-Narrow-Bold', 'Helvetica-Narrow-BoldOblique',
    'Helvetica-Narrow-Oblique', 'NewCenturySchlbk-Bold', 'NewCenturySchlbk-BoldItalic', 'NewCenturySchlbk-Italic',
    'NewCenturySchlbk-Roman', 'Palatino-BoldItalic', 'Palatino-Roman', 'Times-BoldItalic', 'Arial', 'Georgia',
    # Add more fonts as needed
]

fonts = TextClip.list('font')  # Get a list of available fonts
# Create a folder for output
output_folder = "font_samples"
os.makedirs(output_folder, exist_ok=True)

# Generate a text clip for each font
clips = []
for font in fonts:
    try:
        # Generate a TextClip with the name of the font as the text and using the font itself
        clip = TextClip(f"{font}", fontsize=44, color='black', bg_color='chartreuse',  font=font, size=(560, 70))
        clip = clip.set_duration(1)  # Duration of each clip
        clip.write_videofile(f"{output_folder}/{font}.mp4", fps=24)  # Save as video
        clips.append(clip)  # Collect clips to make a single showcase video
    except Exception as e:
        print(f"Failed to create clip for font {font}: {e}")

# Concatenate all clips into one video (optional)
final_clip = concatenate_videoclips(clips)
final_clip.write_videofile(f"{output_folder}/all_fonts.mp4", fps=24)

print("Font clips created.")
