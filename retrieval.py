import os
import shutil
import tempfile
from langchain_community.embeddings import HuggingFaceEmbeddings  
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

FAISS_INDEX_PATH = "./vectorstore/faiss_index"
TEMP_FAISS_INDEX_PATH = "./vectorstore/temp_faiss_index"
DOCUMENTS_PATH = "./documents"

embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

global_retriever = None
temp_retriever = None

def clear_temp_faiss():
    if os.path.exists(TEMP_FAISS_INDEX_PATH):
        print("Removing previous uploaded document FAISS index...")
        shutil.rmtree(TEMP_FAISS_INDEX_PATH)

def load_documents():
    documents = []
    if not os.path.exists(DOCUMENTS_PATH):
        print(f"Documents folder '{DOCUMENTS_PATH}' not found! Creating it now...")
        os.makedirs(DOCUMENTS_PATH)
        return []

    for filename in os.listdir(DOCUMENTS_PATH):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCUMENTS_PATH, filename))
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded {len(docs)} pages from {filename}")

    if not documents:
        print("No legal documents found in the folder!")
    return documents

def create_faiss_index():
    documents = load_documents()
    if not documents:
        print("No documents available to create FAISS index!")
        return None

    print("Creating new FAISS index from legal documents...")
    processed_docs = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)
    vector_store = FAISS.from_documents(processed_docs, embeddings_model)
    
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    vector_store.save_local(FAISS_INDEX_PATH)

    print("FAISS index successfully created and saved!")
    return vector_store

def setup_rag():
    global global_retriever, temp_retriever

    temp_retriever = None
    global_retriever = None

    if os.path.exists(TEMP_FAISS_INDEX_PATH):
        print("Using temporary FAISS retriever (uploaded document).")
        vector_store = FAISS.load_local(TEMP_FAISS_INDEX_PATH, embeddings_model, allow_dangerous_deserialization=True)
        temp_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    if os.path.exists(FAISS_INDEX_PATH):
        print("Using preloaded FAISS retriever (legal documents).")
        vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings_model, allow_dangerous_deserialization=True)
        global_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    print("Legal AI RAG system initialized successfully!")
    return temp_retriever, global_retriever

def process_uploaded_pdf(uploaded_file):
    global temp_retriever

    clear_temp_faiss()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.getvalue())
        temp_pdf_path = temp_pdf.name

    print(f"Processing uploaded PDF: {uploaded_file.name}")

    loader = PyPDFLoader(temp_pdf_path)
    documents = loader.load()

    if not documents:
        print("No text extracted from the uploaded PDF!")
        return temp_retriever

    processed_docs = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)
    print("Creating FAISS index for uploaded document (temporary storage)...")
    vector_store = FAISS.from_documents(processed_docs, embeddings_model)

    os.makedirs(TEMP_FAISS_INDEX_PATH, exist_ok=True)
    vector_store.save_local(TEMP_FAISS_INDEX_PATH)

    print("Uploaded document successfully stored in temporary FAISS database!")

    temp_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    return temp_retriever
