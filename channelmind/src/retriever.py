from typing import List, Dict, Any, Optional

from src.embed_store import get_embedding, get_chroma_collection


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 6,
    video_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant transcript chunks from ChromaDB.

    If video_id is provided, search only inside that video.
    """

    collection = get_chroma_collection()
    query_embedding = get_embedding(query)

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    if video_id:
        query_kwargs["where"] = {"video_id": video_id}

    results = collection.query(**query_kwargs)

    retrieved = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, metadata, distance in zip(documents, metadatas, distances):
        retrieved.append(
            {
                "text": doc,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved