import re

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

#### INDEXING ####

# Load Documents (local files, no web requests)
loaders = [
    PyPDFLoader("test_documents/MaryOliver.pdf"),
    Docx2txtLoader("test_documents/Transcendentalism.docx"),
    TextLoader("test_documents/computer_history.txt"),
]
docs = [doc for loader in loaders for doc in loader.load()]

# pypdf emits one word per line for some PDFs; collapse whitespace so chunks
# contain real content instead of newlines
for doc in docs:
    doc.page_content = re.sub(r"\s+", " ", doc.page_content).strip()

# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
splits = text_splitter.split_documents(docs)

# Embed (Ollama embeddings - requires `ollama pull mxbai-embed-large`)
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OllamaEmbeddings(model="mxbai-embed-large"),
)

retriever = vectorstore.as_retriever(
    search_type="mmr", search_kwargs={"k": 8, "fetch_k": 30}
)

#### RETRIEVAL and GENERATION ####

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
llm = ChatOllama(model="qwen2.5:7b", temperature=0)

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

# Question
print(rag_chain.invoke("What awards did Mary Oliver win?"))
