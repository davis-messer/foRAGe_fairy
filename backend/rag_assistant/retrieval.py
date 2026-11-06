"""
Retrieval. Returns a retriever that fetches chunks from the vector store using MMR (Maximal 
Marginal Relevance) to diversify results. Optionally restricts to chunks from specific files.

Search. get_retriever(sources) returns an MMR retriever (it picks relevant but varied chunks) and 
can be limited to specific file names. retriever is the unfiltered default.
"""

from .config import RETRIEVER_FETCH_K, RETRIEVER_K
from .index import vectorstore


def get_retriever(sources: list[str] | None = None):
    """MMR retriever, optionally restricted to chunks from the given file names."""
    search_kwargs = {"k": RETRIEVER_K, "fetch_k": RETRIEVER_FETCH_K}
    if sources is not None:
        search_kwargs["filter"] = {"source": {"$in": sources}}
    return vectorstore.as_retriever(search_type="mmr", search_kwargs=search_kwargs)


retriever = get_retriever()
