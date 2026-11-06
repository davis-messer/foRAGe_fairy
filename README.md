# RAG Assistant

Chat with your documents using a local LLM. A FastAPI + LangChain backend (Ollama, Chroma) and a Next.js frontend.

## Layout

```
backend/
  pyproject.toml       Python package + dependencies
  rag_assistant/       RAG pipeline and HTTP API (api.py)
  evals/               eval.py + test_queries.json, run against data/sample_documents
data/
  sample_documents/    tracked sample corpus used by evals and the CLI demo
  uploads/             files uploaded through the UI (gitignored)
frontend/              Next.js + TypeScript UI
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- [Ollama](https://ollama.com) running locally with the models pulled:

  ```bash
  ollama pull qwen2.5:7b
  ollama pull mxbai-embed-large
  ```

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e backend
cd frontend && npm install
```

## Run

Start the API and the frontend together (Ctrl+C stops both):

```bash
./dev.sh
```

Open http://localhost:3000. The API runs on http://localhost:8000, reloads when backend code changes, and indexes everything in `data/uploads/` on startup.

To run them separately instead:

```bash
.venv/bin/uvicorn rag_assistant.api:app --port 8000
cd frontend && npm run dev
```

Environment variables:

- `RAG_UPLOADS_DIR` – where uploads are stored (default `data/uploads`)
- `CORS_ORIGINS` – comma-separated origins allowed to call the API (default `http://localhost:3000,http://127.0.0.1:3000`)
- `NEXT_PUBLIC_API_URL` – API base URL used by the frontend (default `http://localhost:8000`)

## API

- `GET /api/files` – list uploaded files
- `POST /api/files` – upload (multipart field `file`); saves to `data/uploads/` and indexes it
- `DELETE /api/files/{id}` – remove from the index and delete the file
- `POST /api/chat` – `{ "question": "...", "file_ids": ["MaryOliver.pdf"] }` → `{ "answer": "...", "sources": [...] }`

## Evals and CLI demo

```bash
.venv/bin/python backend/evals/eval.py   # score test_queries.json against the sample documents
.venv/bin/python -m rag_assistant        # ask one sample question
```
