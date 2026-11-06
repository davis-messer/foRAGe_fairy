"""
FastAPI server for the frontend. On startup it indexes everything in data/uploads. CORS allows 
localhost:3000 by default (the CORS_ORIGINS env var changes this). Routes: GET /api/files (list), 
POST /api/files (upload and index), DELETE /api/files/{id} (remove), and POST /api/chat (ask a 
question about the files you selected).


HTTP API for the frontend. Run with:
    uvicorn rag_assistant.api:app --port 8000
"""

import os
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import UPLOADS_DIR
from .generation import answer
from .index import (
    SUPPORTED_EXTENSIONS,
    add_document,
    index_directory,
    is_supported,
    remove_document,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    index_directory(UPLOADS_DIR)
    yield


app = FastAPI(title="RAG Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


class FileInfo(BaseModel):
    id: str
    name: str
    size: int
    uploaded_at: datetime


class ChatRequest(BaseModel):
    question: str
    file_ids: list[str]


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


def _file_info(path: Path) -> FileInfo:
    stat = path.stat()
    return FileInfo(
        id=path.name,
        name=path.name,
        size=stat.st_size,
        uploaded_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
    )


def _upload_path(file_id: str) -> Path:
    path = UPLOADS_DIR / Path(file_id).name
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")
    return path


@app.get("/api/files", response_model=list[FileInfo])
def list_files():
    paths = [p for p in UPLOADS_DIR.iterdir() if p.is_file() and is_supported(p)]
    return sorted(
        (_file_info(p) for p in paths), key=lambda f: f.uploaded_at, reverse=True
    )


@app.post("/api/files", response_model=FileInfo)
def upload_file(file: UploadFile):
    name = Path(file.filename or "").name
    path = UPLOADS_DIR / name
    if not name or not is_supported(path):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}",
        )
    with path.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    try:
        add_document(path)
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Could not index {name}: {exc}")
    return _file_info(path)


@app.delete("/api/files/{file_id}", status_code=204)
def delete_file(file_id: str):
    path = _upload_path(file_id)
    remove_document(path.name)
    path.unlink()


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")
    if not request.file_ids:
        raise HTTPException(
            status_code=400, detail="Select at least one document to chat about."
        )
    text, sources = answer(question, [Path(f).name for f in request.file_ids])
    return ChatResponse(answer=text, sources=sources)
