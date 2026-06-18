from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from app.database import db_manager
from app.utils.auth_utils import hash_password, verify_password, create_access_token
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    points: int
    level: int
    badges: List[str]
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

@router.post("/register", response_model=TokenResponse)
async def register(user_in: UserRegister):
    # Check if user exists
    existing = await db_manager.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed = hash_password(user_in.password)
    
    # Create user dictionary
    user_data = {
        "username": user_in.username,
        "email": user_in.email.lower(),
        "hashed_password": hashed,
        "points": 0,
        "level": 1,
        "badges": [],
        "created_at": datetime.utcnow().isoformat()
    }
    
    user = await db_manager.create_user(user_data)
    
    # Create token
    access_token = create_access_token({"sub": user["id"]})
    
    # Format response
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "points": user["points"],
            "level": user["level"],
            "badges": user["badges"],
            "created_at": user["created_at"]
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db_manager.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
        
    access_token = create_access_token({"sub": user["id"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "points": user["points"],
            "level": user["level"],
            "badges": user["badges"],
            "created_at": user["created_at"]
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "points": current_user["points"],
        "level": current_user["level"],
        "badges": current_user["badges"],
        "created_at": current_user["created_at"]
    }

@router.post("/logout")
async def logout():
    return {"detail": "Successfully logged out"}
