from openai import OpenAI 
from datetime import datetime
import uuid
from pydantic import BaseModel
from typing import List


class SubtitleSegment(BaseModel):
    word: str
    start: float
    end: float
    
class Subtitles(BaseModel):
    subtitles: List[SubtitleSegment]

class Utils():

    @staticmethod
    def get_time() -> str:
        time = datetime.now()
        return time.strftime("%H-%M-%S")

    def short_uuid(self) -> str:
        return str(uuid.uuid4()).split("-")[0]

    def get_id(self) -> str:
        return f"{self.short_uuid()}-{self.get_time()}"


class Transcription():
    def __init__(self):
        self.client = OpenAI()

    def transcribe_audio(self, full_audio_file_path: str):
        audio_file = open(full_audio_file_path, "rb")
        transcript = self.client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
        return transcript

    def get_subtitles(self, full_audio_file_path: str, merge: bool = True) -> Subtitles:
        print(f"Creating subtitles for {full_audio_file_path}")
        transcript = self.transcribe_audio(full_audio_file_path)
        subtitles = Subtitles(subtitles=transcript.words)
        subtitles = self.add_dots(subtitles)
        subtitles = self.merge_subtitles(subtitles) if merge else subtitles
        return subtitles

    def print_subtitles(self, subtitles: Subtitles, format_text=False) -> None:
        text = ""

        if format_text:
            for subtitle_segment in subtitles.subtitles:
                text += f"{subtitle_segment.word} "
        else:
            for subtitle_segment in subtitles.subtitles:
                text += f"{subtitle_segment.word} {subtitle_segment.start} to {subtitle_segment.end}\n"

        print(text)
    
    def add_dots(self, subtitles: Subtitles, treshold_delta: float = 2.0) -> Subtitles:
        new_subtitles = Subtitles(subtitles=[])
        for subtitle_segment in subtitles.subtitles:
            delta = subtitle_segment.end - subtitle_segment.start
            # print(f"delta: {delta}")
            if delta > treshold_delta:
                subtitle_segment.word += "..."
            new_subtitles.subtitles.append(subtitle_segment)
        
        return subtitles

    def merge_subtitles(self, subtitles: Subtitles, threshold_delta: float = 0.1) -> Subtitles:
        l = len(subtitles.subtitles)
        new_subtitles = Subtitles(subtitles=[])
        skip = False
        for idx, subtitle in enumerate(subtitles.subtitles):

            if skip:
                skip = False
                continue

            if idx + 1 < l:
                delta = subtitles.subtitles[idx + 1].start - subtitle.end
                if delta < threshold_delta:
                    word = f"{subtitle.word} {subtitles.subtitles[idx + 1].word}"
                    new_subtitle_segment = SubtitleSegment(word=word, start=subtitle.start, end=subtitles.subtitles[idx + 1].end)
                    new_subtitles.subtitles.append(new_subtitle_segment)
                    skip = True
                else:
                    new_subtitles.subtitles.append(subtitle)
            if idx + 1 == l and not skip:
                new_subtitles.subtitles.append(subtitle)
        return new_subtitles 


class TTS():

    def tts(self) -> None:
        response = self.client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Hello world! This is a streaming test.",
        )

        response.stream_to_file("output.mp3")


    @staticmethod
    def save_transcript(transcript: str, name_to_save: str) -> None:
        with open(f"{name_to_save}.txt", "w") as file:
            file.write(transcript)

    @staticmethod
    def p_transcript(transcript) -> None:
        print(type(transcript))
        lines = transcript.words
        print(f"lines: {lines}")
        for line in lines:
            # print(f"type: {type(line)} of {line}")
            print(f'words: {line["word"]} {line["start"]} to {line["end"]}')

        subtitles = Subtitles(subtitles=lines)
        print(subtitles)

def main():
    t = Transcription()
    subtitles = t.get_subtitles(full_audio_file_path="assets/simulation.mp3")
    subtitles = t.add_dots(subtitles)
    t.print_subtitles(subtitles)
    merged_subtitles = t.merge_subtitles(subtitles)
    t.print_subtitles(merged_subtitles)

if __name__ == "__main__":
    main()