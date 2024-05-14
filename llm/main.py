from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
import backoff
from typing import List
from transcription.models import Subtitles, SubtitleSegment

TEMPERATURE = 0
SEED = 0
# LLM_MODEL = "gpt-3.5-turbo"
LLM_MODEL = "gpt-4o-2024-05-13"


class RateLimitException(Exception):
    pass


def on_backoff(details):
    print(f"Rate limit exceeded, retrying in {details['wait']:0.1f} seconds...")


class SelectedEmoji(BaseModel):
    emoji: List[str] = Field(..., title="List of relevent emojis. Max 1")
    censored_curse_text: str | None = Field(None, title="Censored text")
    censored_text: bool = Field(False, title="If the text was censored")


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
        system_task = "Return relevent 1 emoji; censor only heavy curse words like this: F@#K, SH!T, etc. Only censor heavy words like FUCK, BITCH, WHORE, FAGGOT. Don't change punctuation"
        content = f"Return relevent emojis and censored version for the text: {subtitle_segment.word}."
        resp = self.extract_model(system_task, content, SelectedEmoji)
        print(f">> {subtitle_segment.word} | {resp.emoji} | {resp.censored_curse_text} | {resp.censored_text}")
        return resp

    def get_emojis(self, subtitles: Subtitles) -> Subtitles:
        new_subtitles = Subtitles(subtitles=[])
        for idx, subtitle_segment in enumerate(subtitles.subtitles):
            resp = self.get_emoji(subtitle_segment)
            subtitle_segment.emoji = resp.emoji
            if resp.censored_text:
                subtitle_segment.word = resp.censored_curse_text
                subtitle_segment.censored = True
            new_subtitles.subtitles.append(subtitle_segment)

        return new_subtitles


if __name__ == "__main__":
    client = Client()
    client.get_emoji(SubtitleSegment(word="Hello", start=0, end=1))
    client.get_emojis(
        Subtitles(
            subtitles=[
                SubtitleSegment(word="Hello", start=0, end=1),
                SubtitleSegment(word="this is shit", start=1, end=2),
            ]
        )
    )
