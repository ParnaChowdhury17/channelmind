import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
LOCAL_EMBEDDING_MODEL = os.getenv(
    "LOCAL_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

GENERATION_PROVIDER = os.getenv("GENERATION_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

CHROMA_PATH = os.getenv("CHROMA_PATH", "data/chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "youtube_channel_knowledge")

RAW_DATA_DIR = "data/raw"
TRANSCRIPT_DIR = "data/raw/transcripts"
PROCESSED_DIR = "data/processed"
CHUNKS_PATH = "data/processed/chunks.jsonl"
VIDEOS_PATH = "data/raw/videos.json"