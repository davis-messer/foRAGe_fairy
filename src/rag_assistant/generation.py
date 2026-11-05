from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama

from .config import LLM_MODEL, TEMPERATURE
from .retrieval import retriever

# Prompt (local template instead of hub.pull, which needs LangChain Hub)
prompt = ChatPromptTemplate.from_template(
    "You are an assistant for question-answering tasks. Answer only with information "
    "explicitly stated in the following retrieved context. If the context mentions the "
    "topic but lacks the specific detail asked for, say what the context does contain "
    "and state that the specifics are not provided. If the context does not mention "
    "the topic at all, say you don't know. Use three sentences maximum and keep the "
    "answer concise.\n\n"
    "Question: {question}\n\nContext: {context}\n\nAnswer:"
)

# LLM (local Ollama - requires `ollama pull qwen2.5:7b`)
llm = ChatOllama(model=LLM_MODEL, temperature=TEMPERATURE)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
