# Legal AI Assistant

## Overview

The **Legal AI Assistant** is an AI-powered chatbot designed to provide legal information and assistance based on user queries. It leverages **Retrieval-Augmented Generation (RAG)** with **LangChain** to process legal documents and generate relevant responses. The bot aims to assist users in understanding legal terminology, case laws, and general legal guidance.

## Features

- **Legal Document Retrieval:** Uses RAG to fetch relevant sections from legal documents.
- **Conversational AI:** Provides natural language responses using an LLM.
- **Efficient Query Handling:** Supports various types of legal queries, including case references, contract law, and compliance information.
-**Document upload:** Users can upload documents and get the summarization, answers to queries asked from that context

## Tech Stack

- **Python** (FastAPI/Flask for backend)
- **LangChain** (for RAG implementation)
- **Groq API** (or another LLM API for response generation)
- **Vector Database** (e.g., FAISS, ChromaDB for document retrieval)
- **Streamlit** (for UI)

## Challenges Faced

- **Legal Text Complexity:** Legal documents are often dense and difficult to process using standard NLP techniques.
- **Data Source Reliability:** Ensuring the assistant retrieves accurate and up-to-date legal information.
- **Query Understanding:** Handling diverse legal queries with varying levels of complexity.
- **RAG time taking:** Simple RAG takes a lot of doing embeddings on every run, later sorted out by using FAISS 

## How to Run

### Prerequisites

- Python 3.9+
- Required dependencies (install using `requirements.txt`)

### Installation

```sh
# Clone the repository
git clone https://github.com/yourusername/legal-ai-assistant.git
cd legal-ai-assistant

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```sh
streamlit run legal_ai.py
```

### Configuration

- Set up API keys in `.env` file (e.g., `GROQ_API_KEY``)
- Here as i deployed this project, the api keys are stored in st.secret

## Usage

- Start the application and enter legal queries in the UIt.
- The bot will retrieve relevant legal information and generate responses.
- User can also upload documents and ask queries related to that

## Future Improvements

- **Better Legal Reasoning:** Fine-tune LLM models on legal datasets.
- **Multilingual Support:** Extend support for multiple languages.
- **Case Law Summarization:** Summarize complex legal cases effectively.
  

## Contributing

Feel free to open issues and submit pull requests to improve this project.

## License

[MIT License](LICENSE)

