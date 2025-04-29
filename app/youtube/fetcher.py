import pickle
import logging
from os import path
from pathlib import Path
from youtube_transcript_api import (
    YouTubeTranscriptApi, FetchedTranscript, TranscriptsDisabled, NoTranscriptFound,
)

logger = logging.getLogger(__name__)

PICKLE_DIR = Path(__file__).resolve().parents[2] / "data" / "youtube_transcripts"


def fetch_video_transcript(video_id: str, to_pickle: bool) -> FetchedTranscript:
    try:
        yt = YouTubeTranscriptApi()
        transcript = yt.fetch(video_id, languages=["en"])
    except (TranscriptsDisabled, NoTranscriptFound):
        transcript = []

    if to_pickle:
        PICKLE_DIR.mkdir(parents=True, exist_ok=True)
        file_path = PICKLE_DIR / f"{video_id}.pkl"
        with open(file_path, "wb") as f:
            pickle.dump(transcript, f)

    return transcript


def load_video_transcript(video_id: str) -> FetchedTranscript:
    file_path = PICKLE_DIR / f"{video_id}.pkl"
    with open(file_path, "rb") as f:
        return pickle.load(f)


def fetch_video_transcript_with_cache(video_id: str) -> FetchedTranscript:
    file_path = PICKLE_DIR / f"{video_id}.pkl"
    if file_path.exists():
        logger.debug(f"Loading transcript from cache for video {video_id}")
        return load_video_transcript(video_id)
    else:
        logger.debug(f"Fetching transcript for video from YouTube {video_id}")
        return fetch_video_transcript(video_id, to_pickle=True)
