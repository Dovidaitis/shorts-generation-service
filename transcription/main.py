from openai import OpenAI
from datetime import datetime
import uuid
from pydantic import BaseModel
from typing import List
from llm.main import Client
from transcription.models import Subtitles, SubtitleSegment
from utils.utils import Path, Loader
import os



class Utils:
    @staticmethod
    def get_time() -> str:
        time = datetime.now()
        return time.strftime("%H-%M-%S")

    def short_uuid(self) -> str:
        return str(uuid.uuid4()).split("-")[0]

    def get_id(self) -> str:
        return f"{self.short_uuid()}-{self.get_time()}"


class Transcription:
    def __init__(self):
        self.client = OpenAI()
        self.llm = Client()
        self.loader = Loader()
        self.path = Path()

    def transcribe_audio(self, full_audio_file_path: str):
        print(f"TRANSCRIPTION >> Transcribing audio from {full_audio_file_path}")
        audio_file = open(full_audio_file_path, "rb")
        transcript = self.client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
        return transcript

    def get_subtitles(self, full_audio_file_path: str, save_path: str = "subtitles.json", add_emoji: bool = True) -> Subtitles:
        if os.path.exists(save_path):
            print("TRANSCRIPTION >> Loading subtitles from cache")
            subtitles = self.loader.load_from_json(Subtitles, save_path)
            return subtitles
        print(f"TRANSCRIPTION >> Creating subtitles for {full_audio_file_path}")
        transcript = self.transcribe_audio(full_audio_file_path)
        subtitles = Subtitles(subtitles=transcript.words)
        subtitles = self.add_dots(subtitles)
        subtitles = self.merge_subtitles(subtitles) 
        if add_emoji:
            subtitles = self.llm.get_emojis(subtitles)
        self.loader.save_to_json(subtitles, self.path.get_cache_path(save_path))
        return subtitles

    def print_subtitles(self, subtitles: Subtitles, format_text=False) -> None:
        text = ""

        if format_text:
            for subtitle_segment in subtitles.subtitles:
                text += f"{subtitle_segment.word} "

        # Calculate the maximum word length to align the columns
        max_word_length = max(len(subtitle_segment.word) for subtitle_segment in subtitles.subtitles)
        max_emoji_length = max(len(" ".join(subtitle_segment.emoji)) for subtitle_segment in subtitles.subtitles)

        for subtitle_segment in subtitles.subtitles:
            word = subtitle_segment.word
            emoji = " ".join(subtitle_segment.emoji)
            start = subtitle_segment.start
            end = subtitle_segment.end

            # print(f"len of emoji: {len(emoji)} max_emoji_length: {max_emoji_length} emoji: {emoji}")
            if len(emoji) < max_emoji_length:
                emoji += " "* ((max_emoji_length - len(emoji)))
                # print(f"len of emoji: {len(emoji)} max_emoji_length: {max_emoji_length} emoji: *{emoji}*")
            line = f"{word:<{max_word_length}} | {start:07.6f} to {end:07.6f} | {emoji}"
            print(line)

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

    def merge_subtitles(
        self, subtitles: Subtitles, threshold_delta: float = 0.1
    ) -> Subtitles:
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
                    new_subtitle_segment = SubtitleSegment(
                        word=word,
                        start=subtitle.start,
                        end=subtitles.subtitles[idx + 1].end,
                        emoji=subtitle.emoji + subtitles.subtitles[idx + 1].emoji,
                    )
                    new_subtitles.subtitles.append(new_subtitle_segment)
                    skip = True
                else:
                    new_subtitles.subtitles.append(subtitle)
            if idx + 1 == l and not skip:
                new_subtitles.subtitles.append(subtitle)
        return new_subtitles


class TTS:
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
    subtitles = t.get_subtitles(full_audio_file_path="assets/simulation.mp3", save_path="simulation.json")
    t.print_subtitles(subtitles)


if __name__ == "__main__":
    main()
