from typing import List, Dict, Any


def chunk_transcript(
    transcript: List[Dict[str, Any]],
    video: Dict[str, Any],
    chunk_size_words: int = 220,
    overlap_words: int = 50,
) -> List[Dict[str, Any]]:
    """
    Convert transcript snippets into overlapping chunks while preserving timestamps.

    Each chunk will contain:
    - text
    - video_id
    - video_title
    - start_time
    - end_time
    - timestamp_url
    """

    chunks = []
    current_words = []
    current_start = None
    current_end = None
    chunk_index = 0

    for snippet in transcript:
        text = snippet.get("text", "").strip()
        start = float(snippet.get("start", 0.0))
        duration = float(snippet.get("duration", 0.0))
        end = start + duration

        if not text:
            continue

        words = text.split()

        if current_start is None:
            current_start = start

        current_words.extend(words)
        current_end = end

        if len(current_words) >= chunk_size_words:
            chunk_text = " ".join(current_words)

            chunk = {
                "id": f"{video['video_id']}_chunk_{chunk_index:05d}",
                "text": chunk_text,
                "metadata": {
                    "video_id": video["video_id"],
                    "video_title": video["title"],
                    "video_url": video["url"],
                    "start_time": current_start,
                    "end_time": current_end,
                    "timestamp_url": f"https://www.youtube.com/watch?v={video['video_id']}&t={int(current_start)}s",
                    "chunk_index": chunk_index,
                },
            }

            chunks.append(chunk)
            chunk_index += 1

            if overlap_words > 0:
                current_words = current_words[-overlap_words:]
            else:
                current_words = []

            current_start = start
            current_end = end

    if current_words:
        chunk_text = " ".join(current_words)

        chunk = {
            "id": f"{video['video_id']}_chunk_{chunk_index:05d}",
            "text": chunk_text,
            "metadata": {
                "video_id": video["video_id"],
                "video_title": video["title"],
                "video_url": video["url"],
                "start_time": current_start,
                "end_time": current_end,
                "timestamp_url": f"https://www.youtube.com/watch?v={video['video_id']}&t={int(current_start)}s",
                "chunk_index": chunk_index,
            },
        }

        chunks.append(chunk)

    return chunks