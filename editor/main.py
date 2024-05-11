from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, clips_array, ImageClip
from transcription.main import Transcription, SubtitleSegment
import random 
import math
from typing import List
from PIL import Image, ImageFont
import numpy as np
from pilmoji import Pilmoji

emoji_font_path = "/Users/paulius/Library/Fonts/NotoColorEmoji-Regular.ttf"
emoji_font_size = 48

def random_circle_coords(radius, center=(0, 0)):
    theta = random.uniform(0, 2 * math.pi)
    x = radius * math.cos(theta) + center[0]
    y = radius * math.sin(theta) + center[1]
    return [round(x), round(y)]

def make_emoji_image(emoji):
    """Create an image from an emoji using a specific font."""
    emoji_font = ImageFont.truetype(emoji_font_path, emoji_font_size)
    image = Image.new("RGBA", (200, 200), (0, 0, 0, 0))  # Transparent background
    with Pilmoji(image) as pilmoji:
        pilmoji.text((0, 0), emoji.strip(), fill=(0, 0, 0), font=emoji_font)
    return np.array(image.convert('RGBA')) 


def create_subtitle_clip(subtitle: SubtitleSegment, origin):
    FONT_SIZE = 60

    padding_x = 20  # Horizontal padding
    padding_y = 10  # Vertical padding

    txt_clip = TextClip(
        subtitle.word.upper(),
        fontsize=FONT_SIZE,
        color="black",
        font="JetBrainsMono-NF-ExtraBold",
        bg_color="gold",
    )

    txt_width = txt_clip.size[0] + 2 * padding_x
    txt_height = txt_clip.size[1] + 2 * padding_y

    txt_clip = TextClip(
        subtitle.word.upper(),
        fontsize=FONT_SIZE,
        color="black",
        font="JetBrainsMono-NF-ExtraBold",
        bg_color="gold",
        size=(txt_width, txt_height),
    ).set_position("center").set_duration(subtitle.end - subtitle.start).set_start(subtitle.start)

    emoji = subtitle.emoji[0] if subtitle.emoji else "🤔"
    print(f"Creating subtitle clip for '{subtitle.word}' with emoji '{emoji}'")
    # emoji = "🤔"
    emoji_image = make_emoji_image(emoji)
    # print(txt_clip.size)
    position = random_circle_coords(150, center=(origin[0], origin[1]))
    print(position)
    emoji_clip = ImageClip(emoji_image, duration=subtitle.end - subtitle.start).set_start(subtitle.start).set_position(position)

    # Use list to collect clips
    clips = [txt_clip, emoji_clip]
    return clips


def save_audio(video_file_path: str, audio_file_path: str):
    VideoFileClip(video_file_path).audio.write_audiofile(audio_file_path)


def append_additional_video(main_video: CompositeVideoClip, additional_video: CompositeVideoClip) -> CompositeVideoClip:
    # Load the main and additional videos

    # Ensure the additional video is the same length as the main video
    if additional_video.duration > main_video.duration:
        # Calculate the maximum start time for the additional video
        max_start_time = additional_video.duration - main_video.duration
        random_start_time = random.uniform(0, max_start_time)
        # Trim the additional video to the main video's duration
        additional_video = additional_video.subclip(random_start_time, random_start_time + main_video.duration)

    # Stack videos vertically
    final_video = clips_array([[main_video], [additional_video]])
    return final_video


    # Write the final video to a file

def main():
    main_video_path = "assets/simulation.mp4"
    additional_video_path = "assets/parkour.mp4"
    output_path = "output_video_with_additional_c_subtitles.mp4"

    t = Transcription()
    subtitles = t.get_subtitles(full_audio_file_path=main_video_path)
    t.print_subtitles(subtitles)

    main_video = VideoFileClip(main_video_path).subclip(0, 10)
    additional_video = VideoFileClip(additional_video_path).subclip(0, 10)
    origin = (main_video.size[0]//2, main_video.size[1]//2)

    clips = [create_subtitle_clip(sub, origin) for sub in subtitles.subtitles]
    subtitles_clips, emoji_clips = zip(*clips)
    subtitles_clips = list(subtitles_clips)
    emoji_clips = list(emoji_clips)


    composite_vertical_video = append_additional_video(main_video, additional_video)
    final_video = CompositeVideoClip([composite_vertical_video] + subtitles_clips + emoji_clips)
    final_video.write_videofile(output_path, codec="libx264", fps=24)

if __name__ == "__main__":
    main()