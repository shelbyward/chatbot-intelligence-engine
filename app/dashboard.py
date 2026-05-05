import os
import sys
import streamlit as st

# Must be set before any chromadb import
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# On Streamlit Cloud, secrets are loaded from the dashboard settings.
# Locally, llm_utils loads the .env file itself.
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from llm_utils import build_qa_chain, ask

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JTR Chatbot",
    page_icon="🪖",
    layout="centered",
)

# st.cache_resource builds the chain once per server session and reuses it.
# Without this, the vector store would reload on every message (very slow).
@st.cache_resource
def load_chain():
    return build_qa_chain()

chain, retriever = load_chain()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("JTR Chatbot")
st.caption("Ask questions about military travel regulations. Answers are grounded in the Joint Travel Regulations (JTR).")
st.divider()

# ── Chat history ──────────────────────────────────────────────────────────────
# st.session_state persists data between Streamlit reruns (every time the user
# interacts with the page, Streamlit reruns the entire script from top to bottom).
# Without this, the chat history would reset on every message.
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("source_pages"):
            st.caption(f"Sources: JTR pages {message['source_pages']}")

# ── Input ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a JTR question..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching the JTR..."):
            try:
                response = ask(chain, retriever, prompt)
                answer = response["answer"]
                pages = response["source_pages"]
            except Exception as e:
                answer = f"Something went wrong: {e}"
                pages = []

        st.markdown(answer)
        if pages:
            st.caption(f"Sources: JTR pages {pages}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "source_pages": pages,
    })