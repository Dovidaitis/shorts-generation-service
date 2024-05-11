from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, clips_array, ImageClip
from transcription.main import Transcription, SubtitleSegment
import random 
import math
from typing import List
from PIL import Image, ImageFont
import numpy as np
from pilmoji import Pilmoji
from utils.utils import Path
import os

emoji_font_path = "/Users/paulius/Library/Fonts/NotoColorEmoji-Regular.ttf"
emoji_font_size = round(128 * 1.5)

def random_circle_coords(radius, center=(0, 0)):
    theta = random.uniform(0, 2 * math.pi)
    x = radius * math.cos(theta) + center[0]
    y = center[1]
    while abs(y - center[1]) < 120:
        theta = random.uniform(0, 2 * math.pi)
        y = radius * math.sin(theta) + center[1]
        if y > center[1]:
            y *= -1
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

    if subtitle.start > 10:
        return [None, None]

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
    emoji_image = make_emoji_image(emoji)
    position = random_circle_coords(350, center=(origin[0], origin[1]))
    x = (origin[0] + txt_width//2) * 0.80
    y = (origin[1] + txt_height//2) * 1.2
    position = (x, y)
    # print(position)
    emoji_clip = ImageClip(emoji_image, duration=subtitle.end - subtitle.start).set_start(subtitle.start).set_position(position)

    # Use list to collect clips
    clips = [txt_clip, emoji_clip]
    return clips


def generate_audio(video_file_path: str, audio_file_path: str):
    if os.path.exists(audio_file_path):
        print(f"EDITOR >> Audio file already exists -> {audio_file_path}")
        return
    VideoFileClip(video_file_path).audio.write_audiofile(audio_file_path)
    print(f"EDITOR >> Audio file generated -> {audio_file_path}")


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


from moviepy.editor import VideoFileClip

def resize(video_path: str, output_path: str):
    clip = VideoFileClip(video_path)
    
    original_width = clip.size[0]
    original_height = clip.size[1]
    
    target_aspect_ratio = 1080 / 1920
    
    if original_width / original_height > target_aspect_ratio:
        # Width is too large
        new_height = original_height
        new_width = int(target_aspect_ratio * new_height)
    else:
        # Height is too large
        new_width = original_width
        new_height = int(new_width / target_aspect_ratio)
    
    # Calculate crop coordinates (center crop)
    x_center = original_width / 2
    y_center = original_height / 2
    x1 = x_center - new_width / 2
    y1 = y_center - new_height / 2
    
    cropped_clip = clip.crop(x1=x1, y1=y1, width=new_width, height=new_height)
    cropped_clip.write_videofile(output_path, codec='libx264')
    clip.close()
    cropped_clip.close()

def main():
    resize("output_video_with_additional_c_subtitles.mp4", "output.mp4")

def build():
    path = Path(
        raw_name="simulation",
        lower_video_name="parkour_big",
        output_name="additional_subs",
    )

    t = Transcription()
    generate_audio(video_file_path=path.main_video_path, audio_file_path=path.subtitle_audio_path)
    subtitles = t.get_subtitles(full_audio_file_path=path.subtitle_audio_path, save_path=path.subtitle_json_path)
    t.print_subtitles(subtitles)

    main_video = VideoFileClip(path.main_video_path)
    additional_video = VideoFileClip(path.lower_video_path)
    origin = (main_video.size[0]//2, main_video.size[1])

    clips = [create_subtitle_clip(sub, origin) for sub in subtitles.subtitles]
    subtitles_clips, emoji_clips = zip(*clips)
    subtitles_clips = list(subtitles_clips)
    emoji_clips = list(emoji_clips)

    subtitles_clips = [clip for clip in subtitles_clips if clip is not None]
    emoji_clips = [clip for clip in emoji_clips if clip is not None]

    CLIP = main_video.duration
    CLIP = 10

    composite_vertical_video = append_additional_video(main_video, additional_video)
    final_video = CompositeVideoClip([composite_vertical_video] + subtitles_clips + emoji_clips).subclip(0, CLIP)
    final_video.write_videofile(path.output_path, codec="libx264", audio_codec="libmp3lame", fps=24)

if __name__ == "__main__":
    build()