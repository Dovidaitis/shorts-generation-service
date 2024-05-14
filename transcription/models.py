from pydantic import BaseModel
from typing import List


class SubtitleSegment(BaseModel):
    word: str
    start: float
    end: float
    emoji: List[str] = []
    censored: bool = False


class Subtitles(BaseModel):
    subtitles: List[SubtitleSegment]
