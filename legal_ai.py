import streamlit as st
from retrieval import setup_rag, process_uploaded_pdf, get_retriever
from llm_handler import ask_legal_ai

st.set_page_config(page_title="Legal AI Assistant", page_icon="⚖️", layout="centered")

# ------------------ Page Styling ------------------ #
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

if "retrievers_initialized" not in st.session_state:
    setup_rag(use_temp=False)
    st.session_state["retrievers_initialized"] = True


retriever = get_retriever()


if st.button("Submit Query", use_container_width=True):
    if not query.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        docs = retriever.get_relevant_documents(query)
        response, sources = ask_legal_ai(query)

        st.markdown("""
            <h3 style='color: #2E3A59;'>Answer:</h3>
        """, unsafe_allow_html=True)
        st.write(response)

        
