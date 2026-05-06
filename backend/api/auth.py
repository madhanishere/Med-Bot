from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

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