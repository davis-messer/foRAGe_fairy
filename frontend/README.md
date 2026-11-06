# RAG Assistant Frontend

Next.js (App Router) + React + TypeScript UI for chatting with uploaded documents.

Layout: navigation bar (left), uploaded file list (center left), LLM chat (center right).

See the [project README](../README.md) for setup and running the backend.

## Structure

- `app/` – root layout, global styles, and the main page
- `components/` – `NavBar`, `FileList`, `ChatPanel`
- `lib/api.ts` – client for the FastAPI backend (`backend/rag_assistant/api.py`); base URL from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`)
- `lib/types.ts` – shared types

## Scripts

- `npm run dev` – start the dev server
- `npm run build` – production build
- `npm run lint` – ESLint
