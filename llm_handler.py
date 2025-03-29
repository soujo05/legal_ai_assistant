from dotenv import load_dotenv
import os
import requests
from retrieval import setup_rag
load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"

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

    prompt = f"""
    You are an expert Indian legal assistant. Use the following legal context to answer accurately.

    Legal Context from Documents:
    {context}

    User Question:
    {query}

    Guidelines:
    - Prioritize retrieved legal documents.
    - If no relevant documents, answer using general legal knowledge.
    """

    response = requests.post(GROQ_API_URL, json={"model": "llama3-8b-8192", "messages": [{"role": "system", "content": "You are an expert Indian legal assistant."}, {"role": "user", "content": prompt}]}, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response."), sources
    else:
        return f"Error: {response.status_code} - {response.text}", []
