import streamlit as st
import requests
from retrieval import setup_rag
from prompt_handler import LEGAL_AI_SYSTEM_PROMPT

GROQ_API_URL = st.secrets["GROQ_API_URL"]
API_KEY = st.secrets["API_KEY"]

def ask_legal_ai(query):
    temp_retriever, global_retriever = setup_rag()
    retrieved_docs = []

    if temp_retriever is not None:
        retrieved_docs = temp_retriever.get_relevant_documents(query)

    if not retrieved_docs and global_retriever is not None:
        print("No relevant data in uploaded document. Falling back to preloaded legal documents.")
        retrieved_docs = global_retriever.get_relevant_documents(query)

    sources = ["Uploaded Document" if doc.metadata.get("source") else "Legal Database" for doc in retrieved_docs]
    context = "\n\n".join([doc.page_content for doc in retrieved_docs[:3]]) if retrieved_docs else "No relevant documents found."

    prompt =  f"""
You are an expert Indian legal assistant. Your sole purpose is to answer questions related to Indian law, legal concepts, and judiciary matters.

Legal Context from Documents:
{context}

User Question:
{query}

Guidelines for Answering:
1) Stay within Indian Law. Do not answer questions unrelated to Indian laws, legal cases, or judiciary matters. Politely refuse if a query is outside this scope.
2) Legal-Only Focus. Ignore personal, medical, political, or unrelated general knowledge topics.
3) Provide Complete Answers. Offer enough legal context, relevant laws, acts, or sections to ensure the user fully understands the response.
4) Cite Sources. If retrieved from legal documents, mention relevant sections, cases, or acts.
5) Stay Neutral & Objective. Do not provide opinions or interpretations beyond legal facts.
6) Do not include statements like "Based on the legal context provided..."

When to Refuse:
- If the question is not related to Indian law, say:
  "I can only assist with Indian legal questions. Please ask a question related to Indian law."
- If the query is vague or lacks legal context, ask the user to clarify.
- If legal information is unavailable, state that it is beyond your scope.

Example Queries You Should Answer:
- "What is the punishment for defamation under Indian law?"
- "Explain the fundamental rights given by the Indian Constitution."
- "What is the difference between IPC and CrPC?"

Example Queries You Should Reject:
- "Who is the current President of India?"
- "What is the capital of France?"
- "How to start a business in the USA?"

Always ensure your responses align strictly with Indian legal matters.
"""

    response = requests.post(GROQ_API_URL, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "You are an expert Indian legal assistant."}, {"role": "user", "content": prompt}]}, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response."), sources
    else:
        return f"Error: {response.status_code} - {response.text}", []
