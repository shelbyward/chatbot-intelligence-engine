import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_utils import build_qa_chain, ask

# FastAPI creates the web server. The description shows up in auto-generated API docs.
app = FastAPI(
    title="JTR Chatbot API",
    description="Q&A chatbot for military travel regulations using the Joint Travel Regulations (JTR).",
    version="1.0.0",
)

# CORS lets the Streamlit frontend (running on a different port) call this API.
# Without it, browsers block cross-origin requests by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build the chain once when the server starts — not on every request.
# This avoids reloading ChromaDB on every question (which would be very slow).
print("Loading JTR Q&A chain...")
chain, retriever = build_qa_chain()
print("API ready.")


# Pydantic model defines and validates the shape of incoming request JSON.
# If the request is missing "question", FastAPI automatically returns a 422 error.
class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    source_pages: list


@app.get("/")
def root():
    return {"status": "JTR Chatbot API is running"}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    # research: HTTP POST, request/response cycle, JSON
    response = ask(chain, retriever, request.question)
    return AnswerResponse(
        answer=response["answer"],
        source_pages=response["source_pages"],
    )