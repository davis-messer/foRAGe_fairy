"""
All the settings in one place, easy to find and modify. Includes paths, models, chunking, retrieval,
and temperature settings.
"""

import os
from pathlib import Path

# Project Paths for sample documents and uploads
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

# Tracked sample corpus used by evals and the CLI demo
SAMPLE_DOCUMENTS_DIR = DATA_DIR / "sample_documents"

# Where files uploaded through the API are stored (gitignored)
UPLOADS_DIR = Path(os.environ.get("RAG_UPLOADS_DIR", DATA_DIR / "uploads"))

# Model for LLM answers AND embeddings
LLM_MODEL = "qwen2.5:7b"
EMBEDDING_MODEL = "mxbai-embed-large"

# Chunking Specs
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Retrieval Specs
RETRIEVER_K = 8
RETRIEVER_FETCH_K = 30

TEMPERATURE = 0