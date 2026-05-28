import os
import shutil
import time
from dotenv import load_dotenv

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def rebuild_knowledge_base():

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    raw_docs_dir = os.path.join(BASE_DIR, "data", "raw_documents")
    db_path = os.path.join(BASE_DIR, "data", "vector_store")

    if os.path.exists(db_path):
        shutil.rmtree(db_path)

    documents = []

    for filename in os.listdir(raw_docs_dir):

        file_path = os.path.join(raw_docs_dir, filename)

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

        elif filename.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())

    if not documents:
        print("No documents found.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vector_store = None
    batch_size = 80 # Process 80 chunks at a time

    print(f"Total chunks to embed: {len(chunks)}")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        print(f"Embedding batch {i // batch_size + 1} of {(len(chunks) - 1) // batch_size + 1}...")
        
        try:
            if vector_store is None:
                vector_store = FAISS.from_documents(batch, embeddings)
            else:
                vector_store.add_documents(batch)
        except Exception as e:
            if "429" in str(e):
                print("Rate limit hit! Sleeping for 60 seconds...")
                time.sleep(60)
                # Retry the batch
                if vector_store is None:
                    vector_store = FAISS.from_documents(batch, embeddings)
                else:
                    vector_store.add_documents(batch)
            else:
                raise e

        # Sleep to avoid hitting the 100 requests/min rate limit
        time.sleep(10)

    vector_store.save_local(db_path)
    print("Database built successfully!")



    return vector_store


if __name__ == "__main__":
    rebuild_knowledge_base()