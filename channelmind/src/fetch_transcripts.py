import os
from typing import Dict, Any, List, Optional

from youtube_transcript_api import YouTubeTranscriptApi

from src.utils import save_json
from src.config import TRANSCRIPT_DIR


def fetch_transcript(
    video_id: str,
    languages: Optional[List[str]] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch transcript for a single YouTube video.

    Each transcript item contains:
    - text
    - start
    - duration
    """

    if languages is None:
        languages = ["en"]

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=languages)

        return transcript.to_raw_data()

    except Exception as e:
        print(f"[Transcript Failed] {video_id}: {type(e).__name__}: {e!r}")
        return None


def save_transcript(video_id: str, transcript: List[Dict[str, Any]]) -> str:
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    path = os.path.join(TRANSCRIPT_DIR, f"{video_id}.json")
    save_json(transcript, path)

    return path