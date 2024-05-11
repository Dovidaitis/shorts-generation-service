from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
import backoff
from typing import List
from transcription.models import Subtitles, SubtitleSegment

TEMPERATURE = 0
SEED = 0
LLM_MODEL = "gpt-3.5-turbo"


class RateLimitException(Exception):
    pass


def on_backoff(details):
    print(f"Rate limit exceeded, retrying in {details['wait']:0.1f} seconds...")


class SelectedEmoji(BaseModel):
    emoji: List[str] = Field(..., title="List of relevent emojis. Max 5")


class Client:
    client = instructor.patch(OpenAI())

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=8,
        giveup=lambda e: not isinstance(e, RateLimitException),
    )
    def extract_model(self, system_task: str, content: str, response_model):
        messages = [
            {"role": "system", "content": system_task},
            {"role": "user", "content": content},
        ]

        try:
            resp = self.client.chat.completions.create(
                model=LLM_MODEL,
                temperature=TEMPERATURE,
                seed=SEED,
                messages=messages,
                response_model=response_model,
            )

            return resp
        except Exception as e:
            if "429" in str(e):
                raise RateLimitException("Rate limit exceeded")
            else:
                raise e

    def get_emoji(self, subtitle_segment: SubtitleSegment):
        system_task = "Your task is to give ONLY relevent emojis for the given text. You may return nothing if the provided emoji wouldn't be engaging. No more than 3"
        content = f"Return relevent emojis for the text: {subtitle_segment.word}"
        resp = self.extract_model(system_task, content, SelectedEmoji)
        print(f">> {subtitle_segment.word} | {resp.emoji}")
        return resp

    def get_emojis(self, subtitles: Subtitles, max_n: int = 15) -> Subtitles:
        new_subtitles = Subtitles(subtitles=[])
        for idx, subtitle_segment in enumerate(subtitles.subtitles):
            if idx >= max_n:
                break
            subtitle_segment.emoji = self.get_emoji(subtitle_segment).emoji
            new_subtitles.subtitles.append(subtitle_segment)

        return new_subtitles


if __name__ == "__main__":
    client = Client()
    client.get_emoji(SubtitleSegment(word="Hello", start=0, end=1))
    client.get_emojis(Subtitles(subtitles=[SubtitleSegment(word="Hello", start=0, end=1), SubtitleSegment(word="World", start=1, end=2), SubtitleSegment(word="!", start=2, end=3)]))
