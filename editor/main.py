from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from transcription.main import Transcription, SubtitleSegment


# Function to create a subtitle clip
def create_subtitle_clip(subtitle: SubtitleSegment):
    FONT_SIZE = 60

    padding_x = 20  # Horizontal padding
    padding_y = 10  # Vertical padding

    txt_clip = TextClip(subtitle.word.upper(), fontsize=FONT_SIZE, color='black', font="JetBrainsMono-NF-ExtraBold", bg_color='gold')
    
    txt_width = txt_clip.size[0] + 2 * padding_x
    txt_height = txt_clip.size[1] + 2 * padding_y
    
    txt_clip = TextClip(subtitle.word.upper(), fontsize=FONT_SIZE, color='black', font="JetBrainsMono-NF-ExtraBold", bg_color='gold',
                        size=(txt_width, txt_height))
    
    txt_clip = txt_clip.set_position('center').set_duration(subtitle.end - subtitle.start).set_start(subtitle.start)
    return txt_clip



def main():
    video = VideoFileClip("assets/simulation.mp4")
    # print(TextClip.list('font'))
    # print(TextClip.list('color'))
    # return
    t = Transcription()
    subtitles = t.get_subtitles(full_audio_file_path="assets/simulation.mp3")
    t.print_subtitles(subtitles)
    # print(f"subtitles: {subtitles}")

    subtitles_clips = [create_subtitle_clip(sub) for sub in subtitles.subtitles]
    # print(f"\n\nSubtitles_clips: {subtitles_clips}")

    final_video = CompositeVideoClip([video] + subtitles_clips)

    final_video.write_videofile("output_video_gold_w_dots.mp4", codec='libx264', fps=60)

if __name__ == "__main__":
    main()
