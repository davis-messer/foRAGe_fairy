from .generation import rag_chain

if __name__ == "__main__":
    print(rag_chain.invoke("What awards did Mary Oliver win?"))
