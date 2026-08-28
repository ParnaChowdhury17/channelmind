"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

const markdownComponents: Components = {
  p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
  strong: ({ children }) => (
    <strong className="font-semibold text-neutral-100">{children}</strong>
  ),
  ul: ({ children }) => (
    <ul className="mb-3 list-disc space-y-1 pl-5">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-3 list-decimal space-y-1 pl-5">{children}</ol>
  ),
  li: ({ children }) => <li>{children}</li>,
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="font-medium text-blue-400 hover:text-blue-300"
    >
      {children}
    </a>
  ),
  code: ({ children }) => (
    <code className="rounded bg-neutral-800 px-1.5 py-0.5 text-sm text-neutral-200">
      {children}
    </code>
  ),
  table: ({ children }) => (
    <div className="mb-3 overflow-x-auto">
      <table className="w-full border-collapse text-sm">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-neutral-800 bg-neutral-900 px-3 py-2 text-left font-medium text-neutral-200">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="border border-neutral-800 px-3 py-2 align-top text-neutral-300">
      {children}
    </td>
  ),
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type Source = {
  video_title: string;
  video_id: string;
  timestamp: string;
  start_time: number;
  end_time: number;
  timestamp_url: string;
  text: string;
  distance: number;
};

type AskResponse = {
  query: string;
  answer: string;
  sources: Source[];
};

type StatsResponse = {
  collection_name: string;
  indexed_chunks: number;
  status: string;
};

type IngestResponse = {
  status: string;
  videos_found: number;
  videos_processed: number;
  videos_skipped: number;
  chunks_created: number;
  total_indexed_chunks: number;
  processed_videos: {
    video_id: string;
    title: string;
    chunks_created: number;
  }[];
  skipped_videos: {
    video_id: string;
    title: string;
    reason: string;
  }[];
};

type IndexedVideo = {
  video_id: string;
  video_title: string;
  video_url: string;
  chunk_count: number;
};

type VideosResponse = {
  count: number;
  videos: IndexedVideo[];
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [data, setData] = useState<AskResponse | null>(null);

  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [statsError, setStatsError] = useState(false);
  const [indexedVideos, setIndexedVideos] = useState<IndexedVideo[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [channelUrl, setChannelUrl] = useState("");
  const [maxVideos, setMaxVideos] = useState(3);
  const [ingesting, setIngesting] = useState(false);
  const [ingestResult, setIngestResult] = useState<IngestResponse | null>(null);
  const [ingestError, setIngestError] = useState("");

  async function fetchStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);

      if (!response.ok) {
        setStatsError(true);
        return;
      }

      const result: StatsResponse = await response.json();
      setStats(result);
      setStatsError(false);
    } catch {
      setStats(null);
      setStatsError(true);
    }
  }

  async function fetchIndexedVideos() {
    try {
      const response = await fetch(`${API_BASE_URL}/videos`);

      if (!response.ok) {
        return;
      }

      const result: VideosResponse = await response.json();
      setIndexedVideos(result.videos);
    } catch {
      setIndexedVideos([]);
    }
  }

  useEffect(() => {
    fetchStats();
    fetchIndexedVideos();
  }, []);

  async function handleIngest() {
    if (!channelUrl.trim()) return;

    setIngesting(true);
    setIngestError("");
    setIngestResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel_url: channelUrl,
          max_videos: maxVideos,
        }),
      });

      if (!response.ok) {
        throw new Error("Ingestion failed");
      }

      const result: IngestResponse = await response.json();
      setIngestResult(result);

      setStats({
        collection_name: "youtube_channel_knowledge",
        indexed_chunks: result.total_indexed_chunks,
        status: "ready",
      });

      await fetchIndexedVideos();
    } catch {
      setIngestError(
        "Could not ingest the channel. Make sure the backend is running and the channel has available transcripts."
      );
    } finally {
      setIngesting(false);
    }
  }

  async function handleAsk() {
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setData(null);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          top_k: topK,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const result: AskResponse = await response.json();
      setData(result);
    } catch {
      setError(
        `Could not connect to the backend at ${API_BASE_URL}.`
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12">
        <div className="space-y-5">
          <p className="text-sm uppercase tracking-[0.35em] text-neutral-400">
            ChannelMind
          </p>

          <h1 className="max-w-4xl text-4xl font-semibold tracking-tight md:text-6xl">
            Ask questions across an entire YouTube channel.
          </h1>

          <p className="max-w-2xl text-lg text-neutral-400">
            A local RAG-powered knowledge engine that searches indexed YouTube
            transcripts and returns grounded answers with timestamped sources.
          </p>

          <div className="grid max-w-3xl gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-neutral-800 bg-neutral-900/70 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">
                Backend
              </p>
              <p
                className={`mt-2 text-lg font-medium ${
                  statsError ? "text-red-400" : "text-green-400"
                }`}
              >
                {stats ? "Online" : statsError ? "Offline" : "Checking..."}
              </p>
            </div>

            <div className="rounded-2xl border border-neutral-800 bg-neutral-900/70 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">
                Indexed Chunks
              </p>
              <p className="mt-2 text-lg font-medium text-neutral-100">
                {stats ? stats.indexed_chunks : "—"}
              </p>
            </div>

            <div className="rounded-2xl border border-neutral-800 bg-neutral-900/70 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">
                Vector Store
              </p>
              <p className="mt-2 truncate text-lg font-medium text-neutral-100">
                {stats ? stats.collection_name : "—"}
              </p>
            </div>
          </div>

          {indexedVideos.length > 0 && (
            <div className="max-w-3xl rounded-3xl border border-neutral-800 bg-neutral-900/70 p-5">
              <div className="mb-4 flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-neutral-500">
                    Indexed Videos
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-neutral-100">
                    {indexedVideos.length} searchable videos
                  </h2>
                </div>

                <button
                  onClick={fetchIndexedVideos}
                  className="rounded-xl border border-neutral-700 px-4 py-2 text-sm text-neutral-300 transition hover:bg-neutral-800"
                >
                  Refresh
                </button>
              </div>

              <div className="space-y-3">
                {indexedVideos.map((video) => (
                  <div
                    key={video.video_id}
                    className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4"
                  >
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-medium text-neutral-100">
                          {video.video_title}
                        </p>
                        <p className="mt-1 text-sm text-neutral-500">
                          {video.chunk_count} chunks indexed
                        </p>
                      </div>

                      <a
                        href={video.video_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm font-medium text-blue-400 hover:text-blue-300"
                      >
                        Open video →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="rounded-3xl border border-neutral-800 bg-neutral-900/80 p-5 shadow-2xl">
          <div className="mb-4">
            <p className="text-sm uppercase tracking-[0.25em] text-neutral-500">
              Index a Channel
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-neutral-100">
              Add YouTube videos to the knowledge base
            </h2>
            <p className="mt-2 text-sm text-neutral-400">
              Paste a channel videos URL. Start with 1–3 videos while testing.
            </p>
          </div>

          <label className="mb-3 block text-sm font-medium text-neutral-300">
            YouTube channel URL
          </label>

          <input
            value={channelUrl}
            onChange={(e) => setChannelUrl(e.target.value)}
            placeholder="https://www.youtube.com/@3blue1brown/videos"
            className="w-full rounded-2xl border border-neutral-700 bg-neutral-950 p-4 text-base text-neutral-100 outline-none placeholder:text-neutral-600 focus:border-neutral-500"
          />

          <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <label className="text-sm text-neutral-400">Max videos</label>
              <input
                type="range"
                min="1"
                max="10"
                value={maxVideos}
                onChange={(e) => setMaxVideos(Number(e.target.value))}
              />
              <span className="rounded-full bg-neutral-800 px-3 py-1 text-sm">
                {maxVideos}
              </span>
            </div>

            <button
              onClick={handleIngest}
              disabled={ingesting}
              className="rounded-2xl bg-neutral-100 px-6 py-3 font-medium text-neutral-950 transition hover:bg-neutral-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {ingesting ? "Indexing..." : "Index Channel"}
            </button>
          </div>

          {ingestError && (
            <p className="mt-4 rounded-2xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
              {ingestError}
            </p>
          )}

          {ingestResult && (
            <div className="mt-4 rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
              <p className="font-medium text-green-400">
                Ingestion completed
              </p>

              <div className="mt-3 grid gap-3 text-sm text-neutral-300 sm:grid-cols-4">
                <div>
                  <p className="text-neutral-500">Found</p>
                  <p className="text-lg font-semibold">
                    {ingestResult.videos_found}
                  </p>
                </div>

                <div>
                  <p className="text-neutral-500">Processed</p>
                  <p className="text-lg font-semibold">
                    {ingestResult.videos_processed}
                  </p>
                </div>

                <div>
                  <p className="text-neutral-500">Chunks Created</p>
                  <p className="text-lg font-semibold">
                    {ingestResult.chunks_created}
                  </p>
                </div>

                <div>
                  <p className="text-neutral-500">Total Indexed</p>
                  <p className="text-lg font-semibold">
                    {ingestResult.total_indexed_chunks}
                  </p>
                </div>
              </div>

              {ingestResult.processed_videos.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-sm font-medium text-neutral-400">
                    Processed videos
                  </p>

                  {ingestResult.processed_videos.map((video) => (
                    <div
                      key={video.video_id}
                      className="rounded-xl border border-neutral-800 bg-neutral-900 p-3 text-sm"
                    >
                      <p className="font-medium text-neutral-200">
                        {video.title}
                      </p>
                      <p className="text-neutral-500">
                        {video.chunks_created} chunks
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {ingestResult.skipped_videos.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-sm font-medium text-yellow-400">
                    Skipped videos
                  </p>

                  {ingestResult.skipped_videos.map((video) => (
                    <div
                      key={video.video_id}
                      className="rounded-xl border border-yellow-900 bg-yellow-950/30 p-3 text-sm"
                    >
                      <p className="font-medium text-neutral-200">
                        {video.title}
                      </p>
                      <p className="text-yellow-300">{video.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="rounded-3xl border border-neutral-800 bg-neutral-900/80 p-5 shadow-2xl">
          <label className="mb-3 block text-sm font-medium text-neutral-300">
            Your question
          </label>

          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: What is the hairy ball theorem?"
            className="min-h-32 w-full resize-none rounded-2xl border border-neutral-700 bg-neutral-950 p-4 text-base text-neutral-100 outline-none placeholder:text-neutral-600 focus:border-neutral-500"
          />

          <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <label className="text-sm text-neutral-400">Sources</label>
              <input
                type="range"
                min="3"
                max="12"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
              />
              <span className="rounded-full bg-neutral-800 px-3 py-1 text-sm">
                {topK}
              </span>
            </div>

            <button
              onClick={handleAsk}
              disabled={loading}
              className="rounded-2xl bg-white px-6 py-3 font-medium text-neutral-950 transition hover:bg-neutral-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Thinking..." : "Ask ChannelMind"}
            </button>
          </div>

          {error && (
            <p className="mt-4 rounded-2xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
              {error}
            </p>
          )}
        </div>

        {data && (
          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <section className="rounded-3xl border border-neutral-800 bg-neutral-900/80 p-6">
              <p className="mb-3 text-sm uppercase tracking-[0.25em] text-neutral-500">
                Answer
              </p>

              <div className="leading-7 text-neutral-200">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                  {data.answer}
                </ReactMarkdown>
              </div>
            </section>

            <section className="rounded-3xl border border-neutral-800 bg-neutral-900/80 p-6">
              <p className="mb-4 text-sm uppercase tracking-[0.25em] text-neutral-500">
                Timestamped Sources
              </p>

              <div className="space-y-4">
                {data.sources.map((source, index) => (
                  <div
                    key={`${source.video_id}-${source.start_time}-${index}`}
                    className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4"
                  >
                    <div className="mb-2 flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-medium text-neutral-100">
                          {source.video_title}
                        </h3>
                        <p className="text-sm text-neutral-500">
                          Timestamp: {source.timestamp}
                        </p>
                      </div>

                      <span className="rounded-full bg-neutral-800 px-2 py-1 text-xs text-neutral-400">
                        {source.distance.toFixed(3)}
                      </span>
                    </div>

                    <p className="mb-3 line-clamp-4 text-sm leading-6 text-neutral-400">
                      {source.text}
                    </p>

                    <a
                      href={source.timestamp_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-blue-400 hover:text-blue-300"
                    >
                      Open on YouTube →
                    </a>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </section>
    </main>
  );
}