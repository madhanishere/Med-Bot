from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from services.database import SessionLocal, ChatLog

router = APIRouter(tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login_endpoint(request: LoginRequest):
    ADMIN_USER = os.getenv("ADMIN_USER")
    ADMIN_PASS = os.getenv("ADMIN_PASS")
    
    if request.username == ADMIN_USER and request.password == ADMIN_PASS:
        return {"status": "success", "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@router.get("/logs")
async def get_logs():
    db = SessionLocal()
    try:
        logs = db.query(ChatLog).order_by(ChatLog.timestamp.desc()).limit(100).all()
        return [{"timestamp": log.timestamp, "role": log.role, "question": log.question, "answer": log.answer} for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()