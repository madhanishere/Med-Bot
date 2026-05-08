from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.database import SessionLocal, ChatLog

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    question: str
    role: str = "Visitor"


@router.post("/chat")
async def chat_endpoint(chat_request: ChatRequest, request: Request):

    rag_chain = request.app.state.rag_chain

    if not rag_chain:
        raise HTTPException(status_code=500, detail="AI is not initialized.")

    response = request.app.state.rag_chain.invoke(
        {"input": chat_request.question, "role": chat_request.role}
    )
    answer = response["answer"]

    db = SessionLocal()
    try:
        new_log = ChatLog(
            role=chat_request.role, question=chat_request.question, answer=answer
        )
        db.add(new_log)
        db.commit()
    finally:
        db.close()

    return {"answer": answer}
