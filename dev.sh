#!/usr/bin/env bash
# Starts the FastAPI backend (port 8000) and the Next.js frontend (port 3000) together.
# Ctrl+C stops both; if either one exits, the other is stopped too.
set -uo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/uvicorn ]; then
  echo "Backend not installed. Run: python3 -m venv .venv && .venv/bin/pip install -e backend" >&2
  exit 1
fi
if [ ! -d frontend/node_modules ]; then
  echo "Frontend not installed. Run: (cd frontend && npm install)" >&2
  exit 1
fi
if ! curl -sf http://localhost:11434 >/dev/null; then
  echo "Warning: Ollama doesn't appear to be running on localhost:11434 (start it with 'ollama serve')." >&2
fi

kill_tree() {
  local child
  for child in $(pgrep -P "$1"); do
    kill_tree "$child"
  done
  kill -TERM "$1" 2>/dev/null
}

pids=()
cleanup() {
  trap - INT TERM EXIT
  for pid in "${pids[@]}"; do
    kill_tree "$pid"
  done
  wait 2>/dev/null
}
trap cleanup INT TERM EXIT

.venv/bin/uvicorn rag_assistant.api:app --port 8000 --reload --reload-dir backend &
pids+=($!)
npm --prefix frontend run dev &
pids+=($!)

while kill -0 "${pids[0]}" 2>/dev/null && kill -0 "${pids[1]}" 2>/dev/null; do
  sleep 1
done
