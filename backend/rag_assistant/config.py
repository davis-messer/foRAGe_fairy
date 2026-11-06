from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"

LLM_MODEL = "qwen2.5:7b"
EMBEDDING_MODEL = "mxbai-embed-large"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

RETRIEVER_K = 8
RETRIEVER_FETCH_K = 30

TEMPERATURE = 0
