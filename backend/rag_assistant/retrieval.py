from .config import RETRIEVER_FETCH_K, RETRIEVER_K
from .index import vectorstore

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": RETRIEVER_K, "fetch_k": RETRIEVER_FETCH_K},
)
