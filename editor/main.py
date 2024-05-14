from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips,
    clips_array,
    ImageClip,
    vfx
)
from transcription.main import Transcription, SubtitleSegment
import random
import math
from typing import List
from PIL import Image, ImageFont
import numpy as np
from pilmoji import Pilmoji
from utils.utils import Path
import os
import sys
import time

emoji_font_path = "/Users/paulius/Library/Fonts/NotoColorEmoji-Regular.ttf"
emoji_font_size = 180 

SHORT_VIDEO = False 


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
    size = (emoji_font_size, emoji_font_size)
    image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
    with Pilmoji(image) as pilmoji:
        pilmoji.text((0, 0), emoji.strip(), fill=(0, 0, 0), font=emoji_font)
    return np.array(image.convert("RGBA"))


black_jetbrainsMono_gold = {
    "font": "JetBrainsMono-NF-ExtraBold",
    "bg_color": "gold",
    "color": "black",
    "fontsize": 60
}

def create_subtitle_clip(subtitle: SubtitleSegment, origin):
    padding_x = 20  # Horizontal padding
    padding_y = 10  # Vertical padding

    if SHORT_VIDEO and subtitle.start > 10:
        return [None, None]

    txt_clip = TextClip(
        subtitle.word.upper(),
        **black_jetbrainsMono_gold,
    )

    txt_width = txt_clip.size[0] + 2 * padding_x
    txt_height = txt_clip.size[1] + 2 * padding_y

    txt_clip = (
        TextClip(
            subtitle.word.upper(),
            **black_jetbrainsMono_gold,
            size=(txt_width, txt_height),
        )
        .set_position("center")
        .set_duration(subtitle.end - subtitle.start)
        .set_start(subtitle.start)
    )


    emoji = subtitle.emoji[0][0] if subtitle.emoji else "🤔"
    character = emoji.encode('utf-16', 'surrogatepass').decode('utf-16')
    unicode_code = f"{ord(character):04X}"
    print(f"Creating subtitle clip for '{subtitle.word}' with emoji '{emoji} {unicode_code}'")
    emoji_image = make_emoji_image(emoji)
    x = origin[0] - 160 // 2 
    y = origin[1] + 120
    position = (x, y)
    emoji_path = f"assets/ios_emoji_pack/{unicode_code}.png"
    if not os.path.exists(emoji_path):
        print(f"Emoji not found at {emoji_path}. Using default emoji.")
        # emoji_path = f"assets/ios_emoji_pack/1F914.png"
        emoji_clip = None
    else:
        emoji_clip = (
            ImageClip(emoji_path, duration=subtitle.end - subtitle.start)
            .set_start(subtitle.start)
            .set_position(position)
        )

    ANIMATION_DURATION = 0.25
    GROW_FACTOR = 1.15
    EMOJI_DURATION = 0.3
    EMOJI_GROW_FACTOR = 1.05
    new_size_animation = lambda t: 1 + (GROW_FACTOR - 1) * max(0, min(1, 1 - abs(t - ANIMATION_DURATION / 2) / (ANIMATION_DURATION / 2)))
    emoji_animation = lambda t: 1 + (EMOJI_GROW_FACTOR - 1) * max(0, min(1, 1 - abs(t - EMOJI_DURATION / 2) / (EMOJI_DURATION / 2)))
    txt_clip = txt_clip.fx(vfx.resize, newsize=new_size_animation)
    if emoji_clip:
        emoji_clip = emoji_clip.fx(vfx.resize, lambda t: (emoji_animation(t) * emoji_clip.size[0], emoji_animation(t) * emoji_clip.size[1]))


    # Use list to collect clips
    clips = [txt_clip, emoji_clip]
    return clips


def generate_audio(video_file_path: str, audio_file_path: str):
    if os.path.exists(audio_file_path):
        print(f"EDITOR >> Audio file already exists -> {audio_file_path}")
        return
    VideoFileClip(video_file_path).audio.write_audiofile(audio_file_path)
    print(f"EDITOR >> Audio file generated -> {audio_file_path}")


def append_additional_video(
    main_video: CompositeVideoClip, additional_video: CompositeVideoClip
) -> CompositeVideoClip:
    # Load the main and additional videos

    # Ensure the additional video is the same length as the main video
    if additional_video.duration > main_video.duration:
        # Calculate the maximum start time for the additional video
        max_start_time = additional_video.duration - main_video.duration
        random_start_time = random.uniform(0, max_start_time)
        # Trim the additional video to the main video's duration
        additional_video = additional_video.subclip(
            random_start_time, random_start_time + main_video.duration
        )

    # Stack videos vertically
    final_video = clips_array([[main_video], [additional_video]])
    return final_video




def resize(video_path: str):
    clip = VideoFileClip(video_path)

    output_path = f"{video_path.split('.')[0]}_resized.mp4"
    if os.path.exists(output_path):
        print(f"Output file already exists -> {output_path}")
        return

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
    cropped_clip.write_videofile(output_path, audio_codec="aac", fps=30)
    clip.close()
    cropped_clip.close()
    
def recut(video_path: str, segment_duration: int):
    # Ensure the maximum segment duration is no more than 60 seconds
    segment_duration = min(segment_duration, 60)
    clip = VideoFileClip(video_path)

    ranges = []
    clip_duration = clip.duration
    max_duration = int(clip_duration)
    last = False
    prev = 0
    for num in range(0, max_duration, segment_duration):
        if max_duration - num < segment_duration:
            ranges.append((prev, clip_duration))
            last = True
        else:
            ranges.append((prev, num))
        prev = num
    if not last:
        ranges.append((prev, clip_duration))
    ranges.pop(0)
    
    print(ranges)

    for idx, clip_range in enumerate(ranges):
        try:
            print(f"Processing segment {idx+1} of {len(ranges)}...")
            subclip = clip.subclip(*clip_range)
            subclip_path = f"{video_path.split('.')[0]}_recut_pt_{idx+1}.mp4"
            subclip.write_videofile(subclip_path, audio_codec="aac", fps=30)
            time.sleep(1)
        except Exception as e:
            print(f"Error processing segment {idx+1}: {e}", file=sys.stderr)
            continue

def main():
    resize("output_video_with_additional_c_subtitles.mp4", "output.mp4")


def build(resize_video: bool):
    path = Path(
        raw_name="joe",
        lower_video_name="parkour_big",
        output_name="animation",
    )

    t = Transcription()
    generate_audio(
        video_file_path=path.main_video_path, audio_file_path=path.subtitle_audio_path
    )
    subtitles = t.get_subtitles(
        full_audio_file_path=path.subtitle_audio_path, save_path=path.subtitle_json_path
    )
    t.print_subtitles(subtitles)

    main_video = VideoFileClip(path.main_video_path)
    additional_video = VideoFileClip(path.lower_video_path)
    origin = (main_video.size[0] // 2, main_video.size[1])

    clips = [create_subtitle_clip(sub, origin) for sub in subtitles.subtitles]
    subtitles_clips, emoji_clips = zip(*clips)
    subtitles_clips = list(subtitles_clips)
    emoji_clips = list(emoji_clips)

    subtitles_clips = [clip for clip in subtitles_clips if clip is not None]
    emoji_clips = [clip for clip in emoji_clips if clip is not None]

    CLIP = main_video.duration
    if SHORT_VIDEO:
        CLIP = 10

    composite_vertical_video = append_additional_video(main_video, additional_video)
    final_video = CompositeVideoClip(
        [composite_vertical_video] + subtitles_clips + emoji_clips
    ).subclip(0, CLIP)
    final_video.write_videofile(path.output_path, audio_codec="aac", fps=30)
    if resize_video:
        resize(path.output_path)


if __name__ == "__main__":
    build(resize_video=True)
    # recut("output/0511_165916_joe_additional_subs_resized.mp4", 30)
