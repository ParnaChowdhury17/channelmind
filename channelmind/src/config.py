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

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# YouTube blocks transcript requests from most data-center IPs (Railway included).
# Set these to route transcript fetches through a Webshare residential proxy:
# https://www.webshare.io -> purchase a "Residential" package -> dashboard.webshare.io/proxy/settings
WEBSHARE_PROXY_USERNAME = os.getenv("WEBSHARE_PROXY_USERNAME", "")
WEBSHARE_PROXY_PASSWORD = os.getenv("WEBSHARE_PROXY_PASSWORD", "")

CHROMA_PATH = os.getenv("CHROMA_PATH", "data/chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "youtube_channel_knowledge")

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

RAW_DATA_DIR = "data/raw"
TRANSCRIPT_DIR = "data/raw/transcripts"
PROCESSED_DIR = "data/processed"
CHUNKS_PATH = "data/processed/chunks.jsonl"
VIDEOS_PATH = "data/raw/videos.json"