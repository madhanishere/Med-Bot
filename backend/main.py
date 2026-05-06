from fastapi import FastAPI
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

from services.rag_engine import setup_rag_chain 
from api import chat, upload, auth, faq

load_dotenv()

app = FastAPI(title="Med-Bot")

app.state.rag_chain = None

@app.on_event("startup")
async def startup_event():
    db_path = os.path.join("..", "data", "vector_store")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    
    if os.path.exists(db_path):
        vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        app.state.rag_chain = setup_rag_chain(vector_store)

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(auth.router)
app.include_router(faq.router)