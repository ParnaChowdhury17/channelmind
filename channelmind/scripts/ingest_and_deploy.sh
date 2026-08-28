#!/usr/bin/env bash
# Ingest a YouTube channel locally and ship the result to Railway.
#
# Why this exists: YouTube blocks transcript requests from Railway's
# data-center IPs (IpBlocked), so /ingest can't be called against the
# deployed backend directly. The workaround is to ingest from a normal
# residential IP (this machine), commit the resulting data files (they're
# git-tracked and baked into the Railway build image), and redeploy.
#
# Usage: scripts/ingest_and_deploy.sh <channel_url> [max_videos]
# Example: scripts/ingest_and_deploy.sh https://www.youtube.com/@veritasium/videos 5

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <channel_url> [max_videos]" >&2
  exit 1
fi

CHANNEL_URL="$1"
MAX_VIDEOS="${2:-5}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"

cd "$BACKEND_DIR"
# shellcheck disable=SC1091
source venv/bin/activate

echo "==> Ingesting from $CHANNEL_URL (max $MAX_VIDEOS videos)"
python3 scripts/ingest_channel.py "$CHANNEL_URL" "$MAX_VIDEOS"

cd "$REPO_ROOT"

if [ -z "$(git status --porcelain -- channelmind/data)" ]; then
  echo "==> No new data (everything was already indexed). Nothing to deploy."
  exit 0
fi

echo "==> Committing updated data"
git add channelmind/data
git commit -m "Index videos from ${CHANNEL_URL}"

echo "==> Pushing to origin/main"
git push origin main

echo "==> Redeploying Railway"
cd "$BACKEND_DIR"
railway up --ci

echo "==> Done. New content is live at https://channelmind-api-production.up.railway.app"
