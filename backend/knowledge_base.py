import os
import glob
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = os.path.join("..", "data")
DOCS_DIR = os.path.join(DATA_DIR, "raw_documents")
DB_PATH = os.path.join(DATA_DIR, "vector_store")
EMBEDDING_MODEL = "mxbai-embed-large"

def load_all_documents(directory_path: str = DOCS_DIR):
    print(f"[*] Scanning directory for raw documents: {directory_path}")   
    documents = []
    
    for filepath in glob.glob(os.path.join(directory_path, "*.txt")):
        loader = TextLoader(filepath)
        documents.extend(loader.load())
        
    for filepath in glob.glob(os.path.join(directory_path, "*.pdf")):
        loader = PyPDFLoader(filepath)
        documents.extend(loader.load())
        
    if not documents:
        return None
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)
    return text_splitter.split_documents(documents)

def create_vector_store(chunks):
    print(f"[*] Generating embeddings using mxbai-embed-large...")
    print(f"[*] Building FAISS vector database from {len(chunks)} chunks...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    vector_store.save_local(DB_PATH)
    print(f"[+] SUCCESS: FAISS database saved to {DB_PATH}")
    return vector_store

def rebuild_knowledge_base():
    """Triggered by the Admin panel to rebuild the DB when new files are uploaded."""
    chunks = load_all_documents()
    
    if chunks:
        return create_vector_store(chunks)
    return None