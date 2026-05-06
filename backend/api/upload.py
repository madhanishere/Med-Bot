from fastapi import APIRouter, HTTPException, UploadFile, File, Request
import os
import shutil
from backend.services.knowledge_base import rebuild_knowledge_base
from backend.services.rag_engine import setup_rag_chain

router = APIRouter(tags=["Knowledge Base"])

@router.post("/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join("..", "data", "raw_documents", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    vector_store = rebuild_knowledge_base()
    
    if vector_store:

        request.app.state.rag_chain = setup_rag_chain(vector_store)
        return {"message": f"Successfully uploaded {file.filename} and updated knowledge base!"}
        
    raise HTTPException(status_code=500, detail="Failed to rebuild knowledge base.")