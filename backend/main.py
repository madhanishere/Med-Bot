from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from knowledge_base import rebuild_knowledge_base
from rag_engine import setup_rag_chain
import os
import shutil
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Med-Bot")
class FAQRequest(BaseModel):
    content: str
class LoginRequest(BaseModel):
    username: str
    password: str
class ChatRequest(BaseModel):
    question: str
    role: str = "Visitor"

rag_chain = None
LOG_FILE_PATH = os.path.join("..", "data", "chat_logs.txt")

def load_existing_db():
    global rag_chain
    db_path = os.path.join("..", "data", "vector_store")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    if os.path.exists(db_path):
        vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        rag_chain = setup_rag_chain(vector_store)

@app.on_event("startup")
async def startup_event():
    load_existing_db()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="AI is not initialized.")
    
    response = rag_chain.invoke({
        "input": request.question, 
        "role": request.role
    })
    answer = response["answer"]
    

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"Role: {request.role}\nVisitor: {request.question}\nBot: {answer}\n" + "-"*40 + "\n")
        
    return {"answer": answer}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join("..", "data", "raw_documents", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    global rag_chain
    vector_store = rebuild_knowledge_base()
    if vector_store:
        rag_chain = setup_rag_chain(vector_store)
        return {"message": f"Successfully uploaded {file.filename} and updated knowledge base!"}
    raise HTTPException(status_code=500, detail="Failed to rebuild knowledge base.")

def getConntent():
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "No conversation history found."

@app.post("/login")
async def login_endpoint(request: LoginRequest):
    ADMIN_USER = os.getenv("ADMIN_USER")
    ADMIN_PASS = os.getenv("ADMIN_PASS")
    
    if request.username == ADMIN_USER and request.password == ADMIN_PASS:
        return {"status": "success", "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/update-faq")
async def update_faq_endpoint(request: FAQRequest):

    file_path = os.path.join("..", "data", "raw_documents", "ui_quick_updates.txt")
    

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n{request.content}\n")
    

    global rag_chain
    vector_store = rebuild_knowledge_base()
    
    if vector_store:
        rag_chain = setup_rag_chain(vector_store)
        return {"message": "Direct content successfully added to the knowledge base!"}
    else:
        raise HTTPException(status_code=500, detail="Failed to rebuild knowledge base.")
@app.get("/logs")
async def fetch_logs():
    content = getConntent()
    return {"logs": content}