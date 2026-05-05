import streamlit as st
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JTR Chatbot",
    page_icon="🪖",
    layout="centered",
)

API_URL = "http://localhost:8000/ask"

# ── Header ───────────────────────────────────────────────────────────────────
st.title("JTR Chatbot")
st.caption("Ask questions about military travel regulations. Answers are grounded in the Joint Travel Regulations (JTR).")
st.divider()

# ── Chat history ─────────────────────────────────────────────────────────────
# st.session_state persists data between Streamlit reruns (every time the user
# interacts with the page, Streamlit reruns the entire script from top to bottom).
# Without this, the chat history would reset on every message.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("source_pages"):
            st.caption(f"Sources: JTR pages {message['source_pages']}")

# ── Input ─────────────────────────────────────────────────────────────────────
# st.chat_input pins the input box to the bottom of the page like a chat app.
# It returns the user's text when they hit Enter, otherwise returns None.
if prompt := st.chat_input("Ask a JTR question..."):

    # Show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Searching the JTR..."):
            try:
                response = requests.post(API_URL, json={"question": prompt}, timeout=30)
                response.raise_for_status()
                data = response.json()
                answer = data["answer"]
                pages = data["source_pages"]
            except requests.exceptions.ConnectionError:
                answer = "Cannot connect to the API. Make sure the FastAPI server is running (`uvicorn src.main:app --reload --port 8000`)."
                pages = []
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