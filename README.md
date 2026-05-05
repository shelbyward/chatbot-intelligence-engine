# Chatbot Intelligence Engine

A portfolio Q&A chatbot powered by OpenAI GPT and FastAPI.
Ask it anything about my projects, skills, and experience.

## Stack

Python · FastAPI · OpenAI API · LangChain · ChromaDB

## Setup

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Install deps: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your OpenAI key
5. Run: `uvicorn app.main:app --reload`

## Project Structure

- `app/` — FastAPI app and routes
- `src/` — RAG logic, embeddings, vector store
- `data/` — Portfolio knowledge base (markdown/JSON)
