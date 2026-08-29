from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import CHROMA_PATH, COLLECTION_NAME, LOCAL_EMBEDDING_MODEL


_embedding_model = None


def get_local_embedding_model() -> SentenceTransformer:
    """
    Load the local embedding model only once.
    The first run may take time because the model has to download.
    """
    global _embedding_model

    if _embedding_model is None:
        print(f"Loading embedding model: {LOCAL_EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(LOCAL_EMBEDDING_MODEL)

    return _embedding_model


def get_embedding(text: str) -> List[float]:
    """
    Convert text into a vector using a free local SentenceTransformer model.
    """
    model = get_local_embedding_model()

    clean_text = text.replace("\n", " ").strip()
    embedding = model.encode(clean_text, normalize_embeddings=True)

    return embedding.tolist()


def get_chroma_collection():
    """
    Create or load a persistent ChromaDB collection.
    """
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "YouTube channel transcript knowledge base"},
    )

    return collection


def store_chunks(chunks: List[Dict[str, Any]], batch_size: int = 50) -> None:
    """
    Store transcript chunks in ChromaDB.
    """
    collection = get_chroma_collection()

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for chunk in batch:
            ids.append(chunk["id"])
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])
            embeddings.append(get_embedding(chunk["text"]))

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        print(f"Stored batch {i // batch_size + 1}: {len(batch)} chunks")

def rebuild_from_chunks_file(chunks_path: str) -> int:
    """
    Rebuild the ChromaDB collection from the plain-text chunks.jsonl file.

    Used on startup in deployments that don't ship the binary chroma_db
    directory (see rebuild_index.py) - only the JSONL, which is safe to
    commit, is guaranteed to be present.
    """
    from src.utils import load_jsonl

    chunks = load_jsonl(chunks_path)

    deduped = list({chunk["id"]: chunk for chunk in chunks}.values())

    if deduped:
        store_chunks(deduped)

    return len(deduped)


def video_already_indexed(video_id: str) -> bool:
    """
    Check whether at least one chunk from this video already exists in ChromaDB.
    """

    collection = get_chroma_collection()

    results = collection.get(
        where={"video_id": video_id},
        limit=1,
    )

    return len(results.get("ids", [])) > 0

def get_indexed_videos() -> list[dict]:
    """
    Return a unique list of indexed videos from ChromaDB metadata.
    """

    collection = get_chroma_collection()

    results = collection.get(
        include=["metadatas"]
    )

    metadatas = results.get("metadatas", [])

    videos = {}

    for metadata in metadatas:
        video_id = metadata.get("video_id")
        video_title = metadata.get("video_title")
        video_url = metadata.get("video_url")

        if not video_id:
            continue

        if video_id not in videos:
            videos[video_id] = {
                "video_id": video_id,
                "video_title": video_title,
                "video_url": video_url,
                "chunk_count": 0,
            }

        videos[video_id]["chunk_count"] += 1

    return list(videos.values())