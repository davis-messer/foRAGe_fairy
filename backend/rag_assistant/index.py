"""
Ingestion. Loads .pdf, .docx, .txt and .md files, collapses whitespace (some PDFs come out one word 
per line), tags each chunk with its file name, splits the text into chunks, and stores their embeddings 
in an in-memory Chroma vector store. Provides add_document, remove_document and index_directory; a 
thread lock guards writes.
"""

import re
import threading
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL

LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": lambda path: TextLoader(path, encoding="utf-8"),
    ".md": lambda path: TextLoader(path, encoding="utf-8"),
}
SUPPORTED_EXTENSIONS = tuple(LOADERS)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)

# Embed (Ollama embeddings - requires `ollama pull mxbai-embed-large`)
vectorstore = Chroma(embedding_function=OllamaEmbeddings(model=EMBEDDING_MODEL))
_lock = threading.Lock()


def is_supported(path: Path) -> bool:
    return path.suffix.lower() in LOADERS


def load_document(path: Path) -> list[Document]:
    docs = LOADERS[path.suffix.lower()](str(path)).load()
    # pypdf emits one word per line for some PDFs; collapse whitespace so
    # chunks contain real content instead of newlines
    for doc in docs:
        doc.page_content = re.sub(r"\s+", " ", doc.page_content).strip()
        doc.metadata["source"] = path.name
    return [doc for doc in docs if doc.page_content]


def remove_document(name: str) -> None:
    with _lock:
        ids = vectorstore.get(where={"source": name})["ids"]
        if ids:
            vectorstore.delete(ids=ids)


def add_document(path: Path) -> int:
    """Index a file, replacing any chunks previously indexed under its name."""
    splits = text_splitter.split_documents(load_document(path))
    remove_document(path.name)
    if splits:
        with _lock:
            vectorstore.add_documents(splits)
    return len(splits)


def index_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for path in sorted(directory.iterdir()):
        if path.is_file() and is_supported(path):
            add_document(path)
