import json
import os
from typing import Any, Dict, List


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_json(data: Any, path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        ensure_dir(parent)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def append_jsonl(items: List[Dict[str, Any]], path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        ensure_dir(parent)

    with open(path, "a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    items = []

    if not os.path.exists(path):
        return items

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))

    return items


def seconds_to_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"

    return f"{m:02d}:{s:02d}"


def make_youtube_timestamp_url(video_id: str, start_time: float) -> str:
    return f"https://www.youtube.com/watch?v={video_id}&t={int(start_time)}s"