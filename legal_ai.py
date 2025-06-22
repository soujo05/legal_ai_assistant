import streamlit as st
from retrieval import setup_rag, process_uploaded_pdf
from llm_handler import ask_legal_ai

st.set_page_config(page_title="Legal AI Assistant", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
        .title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #2E3A59;
        }
        .query-box {
            border-radius: 10px;
            padding: 10px;
        }
        .upload-box {
            border: 2px dashed #2E3A59;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='title'>⚖️ Legal AI Assistant</p>", unsafe_allow_html=True)

query = st.text_input("Ask a legal question:", key="query_input")

st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a Legal Document (PDF) (Optional)", type="pdf")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    temp_retriever = process_uploaded_pdf(uploaded_file)
    st.session_state["temp_retriever"] = temp_retriever 
    st.success("📄 Uploaded document processed successfully!")

temp_retriever, global_retriever = setup_rag()

if "temp_retriever" in st.session_state:
    temp_retriever = st.session_state["temp_retriever"]

retrieved_docs = []

if temp_retriever is not None:
    retrieved_docs = temp_retriever.invoke(query)

if not retrieved_docs and global_retriever is not None:
    print("No relevant data in uploaded document. Falling back to preloaded legal documents.")
    retrieved_docs = global_retriever.invoke(query)

if st.button("Submit Query", use_container_width=True):
    response, sources = ask_legal_ai(query)
    st.markdown("""
        <h3 style='color: #2E3A59;'>Answer:</h3>
    """, unsafe_allow_html=True)
    st.write(response)

    
