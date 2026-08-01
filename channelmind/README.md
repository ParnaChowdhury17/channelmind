# ChannelMind backend

FastAPI + RAG service for querying YouTube channel transcripts. See the [project README](../README.md) for the full overview, architecture, and setup instructions.

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload
```

## Endpoints

| Method | Path      | Description                                  |
|--------|-----------|-----------------------------------------------|
| GET    | `/`       | Health check                                  |
| GET    | `/stats`  | Indexed chunk count and collection info       |
| GET    | `/videos` | List indexed videos                           |
| POST   | `/ingest` | Ingest a channel's videos into the vector store |
| POST   | `/ask`    | Ask a question, get a grounded answer + sources |

Interactive docs available at `/docs` once the server is running.
