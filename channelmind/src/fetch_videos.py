import yt_dlp
from typing import List, Dict, Any, Optional


def fetch_channel_videos(
    channel_url: str,
    max_videos: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetch video metadata from a YouTube channel, playlist, or videos page.

    Returns a list of:
    - video_id
    - title
    - url
    - duration
    - upload_date
    - channel
    """

    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
        "ignoreerrors": True,
    }

    videos = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

        if not info:
            print("No channel information found.")
            return videos

        entries = info.get("entries", [])

        for entry in entries:
            if entry is None:
                continue

            video_id = entry.get("id")

            if not video_id:
                continue

            video = {
                "video_id": video_id,
                "title": entry.get("title", "Untitled Video"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": entry.get("duration"),
                "upload_date": entry.get("upload_date"),
                "channel": entry.get("channel"),
            }

            videos.append(video)

            if max_videos and len(videos) >= max_videos:
                break

    return videos