import re

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCUMENTS_DIR,
    EMBEDDING_MODEL,
)

# Load Documents (local files, no web requests)
loaders = [
    PyPDFLoader(str(DOCUMENTS_DIR / "MaryOliver.pdf")),
    Docx2txtLoader(str(DOCUMENTS_DIR / "Transcendentalism.docx")),
    TextLoader(str(DOCUMENTS_DIR / "computer_history.txt")),
]
docs = [doc for loader in loaders for doc in loader.load()]

# pypdf emits one word per line for some PDFs; collapse whitespace so chunks
# contain real content instead of newlines
for doc in docs:
    doc.page_content = re.sub(r"\s+", " ", doc.page_content).strip()

# Split
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)
splits = text_splitter.split_documents(docs)

# Embed (Ollama embeddings - requires `ollama pull mxbai-embed-large`)
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OllamaEmbeddings(model=EMBEDDING_MODEL),
)
