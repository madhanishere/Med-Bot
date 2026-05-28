from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services.database import SessionLocal, ChatLog

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    role: str = "Patient"

@router.post("/chat")
async def chat_endpoint(request: Request, payload: ChatRequest):
    rag_chain = request.app.state.rag_chain
    
    if not rag_chain:
        return {"answer": "The database is currently empty or updating.", "citations": []}

    response = rag_chain.invoke({
        "input": payload.message,
        "role": payload.role
    })
    
    citations = []
    if "context" in response:
        for doc in response["context"]:
            source_file = doc.metadata.get("source", "Unknown Document")
            page_num = doc.metadata.get("page", "N/A")
            
            clean_name = source_file.split("/")[-1].split("\\")[-1] 
            
            citations.append({
                "file": clean_name,
                "page": page_num,
                "content_preview": doc.page_content[:150] + "..."
            })

    unique_citations = [dict(t) for t in {tuple(d.items()) for d in citations}]

    # Save to Database
    db = SessionLocal()
    try:
        new_log = ChatLog(
            role=payload.role,
            question=payload.message,
            answer=response["answer"]
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")
        db.rollback()
    finally:
        db.close()

    return {
        "answer": response["answer"],
        "citations": unique_citations
    }