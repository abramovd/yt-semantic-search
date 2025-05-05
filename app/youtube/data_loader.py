import json
from pathlib import Path

from pydantic import BaseModel, Field

YOUTUBE_VIDEOS_JSON_FILE = "youtube_videos.json"
YOUTUBE_VIDEO_URL_PREFIX = "https://www.youtube.com/watch?v="


class Video(BaseModel):
    internal_id: int | None = None
    id: str
    title: str
    meta: dict = Field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"{YOUTUBE_VIDEO_URL_PREFIX}{self.id}"


def load_videos_from_json_file_path(file_path: Path) -> list[Video]:
    with open(file_path) as f:
        data = json.load(f)
    return [Video(**item) for item in data]


def load_videos() -> list[Video]:
    file_path = Path(__file__).resolve().parent / YOUTUBE_VIDEOS_JSON_FILE
    return load_videos_from_json_file_path(file_path)
