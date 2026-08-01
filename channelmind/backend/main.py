from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.embed_store import get_chroma_collection, video_already_indexed, get_indexed_videos
from src.config import COLLECTION_NAME, ALLOWED_ORIGINS
from src.fetch_videos import fetch_channel_videos
from src.fetch_transcripts import fetch_transcript, save_transcript
from src.chunk_transcripts import chunk_transcript
from src.embed_store import store_chunks
from src.utils import save_json, append_jsonl
from src.config import VIDEOS_PATH, CHUNKS_PATH

import sys
import os

# Allow backend/main.py to import from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.retriever import retrieve_relevant_chunks
from src.generator import generate_answer
from src.utils import seconds_to_timestamp


app = FastAPI(
    title="ChannelMind API",
    description="Local RAG API for querying YouTube channel transcripts",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str
    top_k: int = 6
    video_id: str | None = None

class IngestRequest(BaseModel):
    channel_url: str
    max_videos: int = 3


@app.get("/")
def root():
    return {
        "message": "ChannelMind API is running",
        "docs": "/docs",
    }

@app.get("/stats")
def get_stats():
    collection = get_chroma_collection()
    count = collection.count()

    return {
        "collection_name": COLLECTION_NAME,
        "indexed_chunks": count,
        "status": "ready",
    }

@app.get("/videos")
def list_indexed_videos():
    videos = get_indexed_videos()

    return {
        "count": len(videos),
        "videos": videos,
    }

@app.post("/ingest")
def ingest_channel(request: IngestRequest):
    videos = fetch_channel_videos(
        channel_url=request.channel_url,
        max_videos=request.max_videos,
    )

    save_json(videos, VIDEOS_PATH)

    all_chunks = []
    processed_videos = []
    skipped_videos = []

    for video in videos:
        video_id = video["video_id"]

        if video_already_indexed(video_id):
            skipped_videos.append(
                {
                    "video_id": video_id,
                    "title": video["title"],
                    "reason": "Already indexed",
                }
            )
            continue

        transcript = fetch_transcript(video_id)

        if transcript is None:
                skipped_videos.append(
                    {
                        "video_id": video_id,
                        "title": video["title"],
                        "reason": "Transcript unavailable",
                    }
                )
                continue

        save_transcript(video_id, transcript)

        chunks = chunk_transcript(transcript, video)
        all_chunks.extend(chunks)

        processed_videos.append(
            {
                "video_id": video_id,
                "title": video["title"],
                "chunks_created": len(chunks),
            }
        )

    if all_chunks:
        append_jsonl(all_chunks, CHUNKS_PATH)
        store_chunks(all_chunks)

    collection = get_chroma_collection()

    return {
        "status": "completed",
        "videos_found": len(videos),
        "videos_processed": len(processed_videos),
        "videos_skipped": len(skipped_videos),
        "chunks_created": len(all_chunks),
        "total_indexed_chunks": collection.count(),
        "processed_videos": processed_videos,
        "skipped_videos": skipped_videos,
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    chunks = retrieve_relevant_chunks(
    query=request.query,
    top_k=request.top_k,
    video_id=request.video_id,
)

    answer = generate_answer(
        query=request.query,
        chunks=chunks,
    )

    sources = []

    for chunk in chunks:
        metadata = chunk["metadata"]

        sources.append(
            {
                "video_title": metadata["video_title"],
                "video_id": metadata["video_id"],
                "timestamp": seconds_to_timestamp(metadata["start_time"]),
                "start_time": metadata["start_time"],
                "end_time": metadata["end_time"],
                "timestamp_url": metadata["timestamp_url"],
                "text": chunk["text"],
                "distance": chunk["distance"],
            }
        )

    return {
        "query": request.query,
        "answer": answer,
        "sources": sources,
    }