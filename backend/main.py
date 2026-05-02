from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_pipeline import setup_rag_chain
import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

app = FastAPI(title="Hospital FAQ Bot API")


class ChatRequest(BaseModel):
    question: str


rag_chain = None

@app.on_event("startup")
async def startup_event():
    global rag_chain
    db_path = os.path.join("..", "data", "vector_store")
    

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    
    if os.path.exists(db_path):
        print("Loading FAISS database...")

        vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        rag_chain = setup_rag_chain(vector_store)
        print("API is ready!")
    else:
        print("Warning: FAISS database not found. Run rag_pipeline.py first.")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="AI is not initialized.")
    

    response = rag_chain.invoke({"input": request.question})
    return {"answer": response["answer"]}