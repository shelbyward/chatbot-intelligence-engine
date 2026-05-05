# JTR Chatbot — Military Travel Regulations Q&A

A retrieval-augmented generation (RAG) chatbot that answers questions about military travel regulations using the Joint Travel Regulations (JTR). Built with FastAPI, LangChain, ChromaDB, and OpenAI.

Military members can ask plain-English questions and get grounded, cited answers pulled directly from the JTR — without reading 570 pages.

---

## Features

- Answers questions about TDY travel, PCS moves, per diem, lodging, reimbursements, and more
- Every answer cites the JTR page numbers it was drawn from
- Refuses to guess — if the answer is not in the JTR, it says so and directs to the travel office
- Clean chat interface built with Streamlit

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | ChromaDB |
| RAG Framework | LangChain (LCEL) |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| PDF Parsing | PyPDF |

---

## How It Works

```
User question
     ↓
Embed the question (OpenAI)
     ↓
Search ChromaDB for the 5 most relevant JTR chunks
     ↓
Send question + JTR context to GPT-4o-mini
     ↓
Return grounded answer with source page citations
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/chatbot-intelligence-engine.git
cd chatbot-intelligence-engine
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
source venv/bin/activate            # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Open `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
```

### 5. Add the JTR PDF
Download the Joint Travel Regulations PDF from [travel.dod.mil](https://www.travel.dod.mil) and place it at:
```
data/JTR.pdf
```

### 6. Run the ingestion pipeline (one time only)
```bash
python src/processing.py
```
This reads the JTR, splits it into chunks, embeds them, and saves the vector store to `chroma_db/`. Takes a few minutes on first run.

### 7. Start the API server
```bash
uvicorn src.main:app --reload --port 8000
```

### 8. Start the Streamlit UI (separate terminal)
```bash
streamlit run app/dashboard.py
```

Open `http://localhost:8501` in your browser.

---

## Project Structure

```
chatbot-intelligence-engine/
├── app/
│   └── dashboard.py       # Streamlit chat UI
├── src/
│   ├── main.py            # FastAPI backend (/ask endpoint)
│   ├── llm_utils.py       # RAG chain (retrieval + LLM)
│   └── processing.py      # PDF ingestion and ChromaDB setup
├── data/
│   └── JTR.pdf            # Source document (Joint Travel Regulations)
├── .env.example           # Environment variable template
└── requirements.txt       # Python dependencies
```

---

## Example Questions

- *What is the TLE allowance and how many days is it authorized?*
- *Can a member be reimbursed for pet transportation during a PCS move?*
- *How is per diem calculated for TDY travel?*
- *What expenses are reimbursable under the JTR?*