from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
from backend.services.knowledge_base import rebuild_knowledge_base
from backend.services.rag_engine import setup_rag_chain

router = APIRouter(tags=["Knowledge Base"])

class FAQRequest(BaseModel):
    content: str

@router.post("/update-faq")
async def update_faq_endpoint(faq_request: FAQRequest, request: Request):
    file_path = os.path.join("..", "data", "raw_documents", "ui_quick_updates.txt")
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n{faq_request.content}\n")
    
    vector_store = rebuild_knowledge_base()
    
    if vector_store:

        request.app.state.rag_chain = setup_rag_chain(vector_store)
        return {"message": "Content successfully added to the knowledge base!"}
    else:
        raise HTTPException(status_code=500, detail="Failed to rebuild knowledge base.")