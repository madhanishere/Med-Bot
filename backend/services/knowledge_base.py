import os
import shutil

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
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

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(chunks, embeddings)

    vector_store.save_local(db_path)



    return vector_store


if __name__ == "__main__":
    rebuild_knowledge_base()