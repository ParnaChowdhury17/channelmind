from typing import List, Dict, Any
import requests

from src.config import (
    GENERATION_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
)
from src.utils import seconds_to_timestamp


def build_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Convert retrieved chunks into readable context for the local LLM.
    """

    context_blocks = []

    for i, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        timestamp = seconds_to_timestamp(metadata["start_time"])

        block = f"""
SOURCE {i}
Video Title: {metadata["video_title"]}
Timestamp: {timestamp}
URL: {metadata["timestamp_url"]}
Transcript:
{chunk["text"]}
""".strip()

        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)


def generate_answer(query: str, chunks: List[Dict[str, Any]]) -> str:
    """
    Generate an answer using the configured GENERATION_PROVIDER (ollama or groq).
    """

    context = build_context(chunks)

    prompt = f"""
You are ChannelMind, a YouTube channel knowledge assistant.

You must answer using only the transcript sources provided below.

Rules:
1. Do not invent information.
2. If the sources are not enough, say: "The available transcript sources do not provide enough evidence."
3. Mention the relevant video title and timestamp when using a source.
4. Keep the answer clear and structured.
5. Do not mention vector databases, embeddings, or retrieval.

User question:
{query}

Transcript sources:
{context}

Now answer the user question using only the transcript sources.
"""

    if GENERATION_PROVIDER == "groq":
        return _generate_with_groq(prompt)

    return _generate_with_ollama(prompt)


def _generate_with_ollama(prompt: str) -> str:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()


def _generate_with_groq(prompt: str) -> str:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()