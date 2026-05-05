import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "JTR.pdf")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")


def load_and_split_pdf(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages from PDF")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def build_vector_store(chunks):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    print("Embedding chunks and saving to ChromaDB (this may take a few minutes)...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    print(f"Vector store saved to {CHROMA_DIR}")
    return vector_store


def load_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )


if __name__ == "__main__":
    chunks = load_and_split_pdf(PDF_PATH)
    build_vector_store(chunks)
    print("Ingestion complete. You can now run the chatbot.")