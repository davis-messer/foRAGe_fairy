"""
Answering. Holds the prompt, which tells the model to answer only from the retrieved text, say when 
details are missing, and use at most three sentences. Also sets up the Ollama model and two entry 
points: answer(question, sources) returns the answer plus the files it used (the API calls this), 
and rag_chain searches all indexed documents (the demo and evals use this).
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from .config import LLM_MODEL, TEMPERATURE
from .retrieval import get_retriever, retriever

# Prompt (local template instead of hub.pull, which needs LangChain Hub)
prompt = ChatPromptTemplate.from_template(
    "You are an assistant for question-answering tasks. Answer only with information "
    "explicitly stated in the following retrieved context. If the context mentions the "
    "topic but lacks the specific detail asked for, say what the context does contain "
    "and state that the specifics are not provided. If the context does not mention "
    "the topic at all, say you don't know. Keep the answer concise.\n\n"
    "Question: {question}\n\nContext: {context}\n\nAnswer:"
)

# LLM (local Ollama - requires `ollama pull qwen2.5:7b`)
llm = ChatOllama(model=LLM_MODEL, temperature=TEMPERATURE)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


answer_chain = prompt | llm | StrOutputParser()


def answer(question: str, sources: list[str] | None = None) -> tuple[str, list[str]]:
    """Answer a question, returning the answer and the file names it drew on."""
    docs = get_retriever(sources).invoke(question)
    response = answer_chain.invoke(
        {"question": question, "context": format_docs(docs)}
    )
    cited = list(dict.fromkeys(doc.metadata["source"] for doc in docs))
    return response, cited


# Chain
rag_chain = (
    {"context": retriever | format_docs, "question": lambda q: q}
    | answer_chain
)
