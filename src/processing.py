import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "JTR.pdf")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")


def load_and_split_pdf(pdf_path: str):
    # PyPDFLoader reads each page as a separate Document object,
    # preserving the page number in metadata for citations later
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages from PDF")

    # RecursiveCharacterTextSplitter tries to split on paragraph breaks first (\n\n),
    # then line breaks, then sentences, then spaces — so chunks stay semantically intact.
    # chunk_overlap keeps 150 characters of the previous chunk at the start of the next
    # one so no sentence loses context at a boundary.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def build_vector_store(chunks):
    # text-embedding-3-small converts each chunk into a 1536-dimension vector.
    # Similar chunks end up close together in that space
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    print("Embedding chunks and saving to ChromaDB (this may take a few minutes)...")

    # Chroma.from_documents embeds every chunk and writes them to disk at CHROMA_DIR.
    # This only needs to run once — after this the DB persists between sessions.
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    print(f"Vector store saved to {CHROMA_DIR}")
    return vector_store


def load_vector_store():
    # Called at runtime by the chatbot to query the already-built DB.
    # No re-embedding happens here — it just opens the existing store.
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )


if __name__ == "__main__":
    chunks = load_and_split_pdf(PDF_PATH)
    build_vector_store(chunks)
    print("Ingestion complete. You can now run the chatbot.")