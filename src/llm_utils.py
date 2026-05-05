import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from processing import load_vector_store

load_dotenv()

# System prompt keeps answers grounded in JTR text.
# Instructs the model to cite section numbers and dollar amounts when present,
# and to defer to the travel office when the answer is not in the retrieved context.
SYSTEM_PROMPT = """You are a military travel regulations assistant with expertise in the
Joint Travel Regulations (JTR). Answer the question using only the JTR context provided below.
If the answer is not in the context, say "I could not find that in the JTR — please consult
your unit's travel office or the official JTR at travel.dod.mil."

Always be specific: cite dollar amounts, timeframes, and regulation section numbers when present.

Context:
{context}"""


def _format_docs(docs) -> str:
    # Joins retrieved chunks into a single context string for the prompt
    return "\n\n".join(doc.page_content for doc in docs)


def build_qa_chain():
    vector_store = load_vector_store()

    # k=5 retrieves the 5 most semantically similar JTR chunks per question
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    # temperature=0 makes responses deterministic — critical for regulation Q&A
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    # LCEL chain: retrieve -> format -> prompt -> LLM -> parse
    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def ask(chain, retriever, question: str) -> dict:
    answer = chain.invoke(question)

    # Fetch source pages separately for citations
    source_docs = retriever.invoke(question)
    pages = sorted(set(
        doc.metadata.get("page", "unknown") for doc in source_docs
    ))

    return {"answer": answer, "source_pages": pages}


if __name__ == "__main__":
    print("Building Q&A chain...")
    chain, retriever = build_qa_chain()

    test_questions = [
        "What is the standard CONUS per diem rate?",
        "How many days of advance pay is a member authorized for PCS?",
        "Can a member be reimbursed for pet transportation during a PCS move?",
    ]

    for question in test_questions:
        print(f"\nQ: {question}")
        response = ask(chain, retriever, question)
        print(f"A: {response['answer']}")
        print(f"Sources: JTR pages {response['source_pages']}")