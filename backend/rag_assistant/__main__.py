"""
Command-line demo run with python -m rag_assistant. It indexes the sample documents and asks one 
question: "What awards did Mary Oliver win?"
"""

from .config import SAMPLE_DOCUMENTS_DIR
from .generation import rag_chain
from .index import index_directory


if __name__ == "__main__":
    index_directory(SAMPLE_DOCUMENTS_DIR)
    print(rag_chain.invoke("What awards did Mary Oliver win?"))
