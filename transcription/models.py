from pydantic import BaseModel
from typing import List

class SubtitleSegment(BaseModel):
    word: str
    start: float
    end: float
    emoji: List[str] = []


class Subtitles(BaseModel):
    subtitles: List[SubtitleSegment]
