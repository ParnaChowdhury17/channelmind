import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fetch_videos import fetch_channel_videos
from src.fetch_transcripts import fetch_transcript, save_transcript
from src.chunk_transcripts import chunk_transcript
from src.embed_store import store_chunks, video_already_indexed
from src.utils import save_json, append_jsonl
from src.config import VIDEOS_PATH, CHUNKS_PATH


def ingest_channel(channel_url: str, max_videos: int = 5) -> None:
    print(f"Fetching videos from: {channel_url}")

    videos = fetch_channel_videos(channel_url, max_videos=max_videos)
    save_json(videos, VIDEOS_PATH)

    print(f"Found {len(videos)} videos")

    all_chunks = []

    for index, video in enumerate(videos, start=1):
        video_id = video["video_id"]
        title = video["title"]

        print(f"\n[{index}/{len(videos)}] Processing: {title}")
        print(f"Video ID: {video_id}")

        if video_already_indexed(video_id):
            print("Skipping video because it is already indexed.")
            continue

        transcript = fetch_transcript(video_id)

        if transcript is None:
            print("Skipping video because transcript is unavailable.")
            continue

        save_transcript(video_id, transcript)

        chunks = chunk_transcript(transcript, video)
        all_chunks.extend(chunks)

        print(f"Created {len(chunks)} chunks")

    if not all_chunks:
        print("No chunks created. Nothing to store.")
        return

    append_jsonl(all_chunks, CHUNKS_PATH)

    print(f"\nTotal chunks created: {len(all_chunks)}")
    print("Generating embeddings and storing in ChromaDB...")

    store_chunks(all_chunks)

    print("\nIngestion complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_channel.py <youtube_channel_or_playlist_url> [max_videos]")
        sys.exit(1)

    channel_url = sys.argv[1]
    max_videos = int(sys.argv[2]) if len(sys.argv) >= 3 else 5

    ingest_channel(channel_url, max_videos=max_videos)