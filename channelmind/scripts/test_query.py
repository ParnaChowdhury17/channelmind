import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.retriever import retrieve_relevant_chunks
from src.generator import generate_answer
from src.utils import seconds_to_timestamp


def ask(query: str, top_k: int = 6) -> None:
    print(f"\nQuestion: {query}\n")

    chunks = retrieve_relevant_chunks(query, top_k=top_k)

    if not chunks:
        print("No relevant chunks found.")
        return

    print("Retrieved sources:")
    for i, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        timestamp = seconds_to_timestamp(metadata["start_time"])

        print(f"{i}. {metadata['video_title']} — {timestamp}")
        print(f"   {metadata['timestamp_url']}")
        print(f"   Distance: {chunk['distance']:.4f}")

    print("\nGenerating answer...\n")

    answer = generate_answer(query, chunks)

    print("Answer:")
    print(answer)

    print("\nSources:")
    for i, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        timestamp = seconds_to_timestamp(metadata["start_time"])

        print(f"{i}. {metadata['video_title']} — {timestamp}")
        print(f"   {metadata['timestamp_url']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_query.py <question>")
        sys.exit(1)

    query = sys.argv[1]
    ask(query)