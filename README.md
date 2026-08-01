# ChannelMind

Ask questions across an entire YouTube channel and get grounded answers with timestamped sources. ChannelMind ingests a channel's video transcripts, indexes them in a vector store, and answers questions using retrieval-augmented generation (RAG) — every answer is backed by the specific transcript passages it came from, with links straight to the moment in the video.

**Frontend:** https://channelmind-blond.vercel.app
**Backend / API docs:** https://channelmind-api-production.up.railway.app/docs
**Technical deep dive:** https://claude.ai/code/artifact/90db3941-205a-45bf-9311-dddcc49046f3 — step-by-step architecture, design decisions, and tradeoffs

## How it works

1. **Ingest** — given a YouTube channel URL, fetch video metadata (`yt-dlp`) and transcripts (`youtube-transcript-api`).
2. **Chunk & embed** — split transcripts into overlapping chunks and embed them locally with `sentence-transformers`.
3. **Store** — persist chunks and embeddings in a local ChromaDB collection.
4. **Retrieve** — for a given question, embed the query and pull the most relevant transcript chunks.
5. **Generate** — feed the retrieved chunks to an LLM (Groq in production, Ollama for local dev) with a prompt that constrains it to answer only from the provided sources.
6. **Answer** — return the answer alongside the source video titles, timestamps, and direct YouTube links.

## Stack

- **Backend:** FastAPI, ChromaDB, `sentence-transformers` (embeddings), Groq API / Ollama (generation) — deployed on Railway
- **Frontend:** Next.js (App Router), TypeScript, Tailwind — deployed on Vercel

## Project layout

```
channelmind/
  channelmind/        FastAPI backend
    backend/main.py   API routes (/ask, /ingest, /stats, /videos)
    src/               Ingestion, chunking, embedding, retrieval, generation
    data/              Ingested transcripts + ChromaDB store (demo data included)
  frontend/            Next.js UI
```

## Running locally

### Backend

```bash
cd channelmind
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit as needed — see below
uvicorn backend.main:app --reload
```

By default the backend uses **Ollama** for generation, so either run Ollama locally (`ollama pull llama3.2:3b`) or set `GENERATION_PROVIDER=groq` and `GROQ_API_KEY` in `.env` to use Groq's hosted API instead (get a free key at [console.groq.com](https://console.groq.com/keys)).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # points at http://127.0.0.1:8000 by default
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deployment

- **Backend (Railway):** deployed from `channelmind/` (see `Procfile`), with `GENERATION_PROVIDER=groq`, `GROQ_API_KEY`, and `ALLOWED_ORIGINS` (comma-separated list of allowed frontend origins) set as environment variables.
- **Frontend (Vercel):** deployed from `frontend/`, with `NEXT_PUBLIC_API_BASE_URL` set to the Railway backend URL.
