import os
import shutil
import tempfile
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where retrieval.py lives
DOCUMENTS_PATH = os.path.join(BASE_DIR, "data")

FAISS_INDEX_PATH = os.path.join(BASE_DIR, "vectorstore", "faiss_index")
TEMP_FAISS_INDEX_PATH = os.path.join(BASE_DIR, "vectorstore", "temp_faiss_index")


embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


global_retriever = None
temp_retriever = None



def clear_temp_faiss():
    """Remove the temporary FAISS index if it exists."""
    if os.path.exists(TEMP_FAISS_INDEX_PATH):
        print("Removing previous uploaded document FAISS index...")
        shutil.rmtree(TEMP_FAISS_INDEX_PATH)


def load_documents():
    """Load all legal documents from the ./data folder."""
    documents = []
    if not os.path.exists(DOCUMENTS_PATH):
        print(f"Documents folder '{DOCUMENTS_PATH}' not found! Creating it now...")
        os.makedirs(DOCUMENTS_PATH)
        return []

    for filename in os.listdir(DOCUMENTS_PATH):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCUMENTS_PATH, filename))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = "Global Legal Knowledge" 
            documents.extend(docs)
            print(f"Loaded {len(docs)} pages from {filename}")

    if not documents:
        print("No legal documents found in the folder!")
    return documents


def create_faiss_index():
    """Create FAISS index for global legal documents."""
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


def setup_rag(use_temp: bool = False):
    """
    Initialize RAG system.
    - use_temp=True → load temporary FAISS if available (user uploaded).
    - use_temp=False → ignore temporary FAISS, always use global.
    """
    global global_retriever, temp_retriever

    #temp_retriever = None
    #global_retriever = None

    if use_temp and os.path.exists(TEMP_FAISS_INDEX_PATH):
        print("Using temporary FAISS retriever (uploaded document).")
        vector_store = FAISS.load_local(
            TEMP_FAISS_INDEX_PATH,
            embeddings_model,
            allow_dangerous_deserialization=True
        )
        temp_retriever = vector_store.as_retriever(search_kwargs={"k": 10})

    if os.path.exists(FAISS_INDEX_PATH):
        print("Using preloaded FAISS retriever (legal documents).")
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings_model,
            allow_dangerous_deserialization=True
        )
        global_retriever = vector_store.as_retriever(search_kwargs={"k": 10})

    print("✅ Legal AI RAG system initialized successfully!")
    return temp_retriever, global_retriever


def get_retriever():
    """Choose which retriever to use (temp first if available)."""
    if temp_retriever is not None:
        print("Querying TEMP retriever...")
        return temp_retriever
    elif global_retriever is not None:
        print("Querying GLOBAL retriever...")
        return global_retriever
    else:
        raise RuntimeError("No retriever available! Did you run setup_rag()?")


def process_uploaded_pdf(uploaded_file):
    """
    Process a user-uploaded PDF:
    - Clears old temp FAISS
    - Creates new temp FAISS
    - Automatically refreshes retriever
    """
    global temp_retriever

    clear_temp_faiss()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.getvalue())
        temp_pdf_path = temp_pdf.name

    print(f"Processing uploaded PDF: {uploaded_file.name}")

    loader = PyPDFLoader(temp_pdf_path)
    documents = loader.load()
    for doc in documents:
        doc.metadata["source"] = "Uploaded Document"  # ✅ tagging

    if not documents:
        print("No text extracted from the uploaded PDF!")
        return temp_retriever

    processed_docs = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)
    print("Creating FAISS index for uploaded document (temporary storage)...")
    vector_store = FAISS.from_documents(processed_docs, embeddings_model)

    os.makedirs(TEMP_FAISS_INDEX_PATH, exist_ok=True)
    vector_store.save_local(TEMP_FAISS_INDEX_PATH)

    print("✅ Uploaded document successfully stored in temporary FAISS database!")

    temp_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    # ✅ Refresh RAG setup to prioritize temp retriever
    setup_rag(use_temp=True)

    return temp_retriever

def query_rag(query: str):
    retriever = get_retriever()
    results = retriever.get_relevant_documents(query)

    # 🔍 Debug: show what FAISS actually returned
    for i, doc in enumerate(results):
        print(f"[{i+1}] Source: {doc.metadata.get('source', 'Unknown')} | Preview: {doc.page_content[:100]}...")

    # Pass results to your LLM chain
    return results



