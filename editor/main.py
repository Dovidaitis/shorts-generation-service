from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, clips_array
from transcription.main import Transcription, SubtitleSegment
import random 
import math


def create_subtitle_clip(subtitle: SubtitleSegment) -> TextClip:
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
    )

    txt_clip = (
        txt_clip.set_position("center")
        .set_duration(subtitle.end - subtitle.start)
        .set_start(subtitle.start)
    )
    return txt_clip


def save_audio(video_file_path: str, audio_file_path: str):
    VideoFileClip(video_file_path).audio.write_audiofile(audio_file_path)

def random_circle_coords(n, r, center=(0, 0)):
    coords = []
    for _ in range(n):
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta) + center[0]
        y = r * math.sin(theta) + center[1]
        coords.append((x, y))
    return coords

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

    subtitles_clips = [create_subtitle_clip(sub) for sub in subtitles.subtitles]
    # video_with_subtitles = CompositeVideoClip([VideoFileClip(main_video_path)] + subtitles_clips)

    main_video = VideoFileClip(main_video_path)
    additional_video = VideoFileClip(additional_video_path)

    composite_vertical_video = append_additional_video(main_video, additional_video)
    final_video = CompositeVideoClip([composite_vertical_video] + subtitles_clips)
    final_video.write_videofile(output_path, codec="libx264", fps=60)

if __name__ == "__main__":
    main()