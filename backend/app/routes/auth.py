from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from app.database import db_manager
from app.utils.auth_utils import hash_password, verify_password, create_token, verify_token
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

class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None

@router.post("/register", response_model=TokenPairResponse)
async def register(user_in: UserRegister, response: Response):
    existing = await db_manager.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = hash_password(user_in.password)
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

    access_token = create_token({"sub": user["id"]}, token_type="access")
    refresh_token = create_token({"sub": user["id"]}, token_type="refresh")

    # Save refresh token jti in DB for revocation checks
    payload = verify_token(refresh_token)
    jti = payload.get("jti")
    await db_manager.save_refresh_token(user["id"], jti, payload.get("exp"))

    # Set refresh token in HttpOnly cookie (secure=True in production)
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax", secure=False, max_age=60*60*24*7)

    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user["id"], "username": user["username"], "email": user["email"], "points": user.get("points",0), "level": user.get("level",1), "badges": user.get("badges",[]), "created_at": user.get("created_at")}}

@router.post("/login", response_model=TokenPairResponse)
async def login(credentials: UserLogin, response: Response):
    user = await db_manager.get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.get("hashed_password")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access_token = create_token({"sub": user["id"]}, token_type="access")
    refresh_token = create_token({"sub": user["id"]}, token_type="refresh")

    payload = verify_token(refresh_token)
    jti = payload.get("jti")
    await db_manager.save_refresh_token(user["id"], jti, payload.get("exp"))

    # Set refresh token cookie
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax", secure=False, max_age=60*60*24*7)

    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user["id"], "username": user["username"], "email": user["email"], "points": user.get("points",0), "level": user.get("level",1), "badges": user.get("badges",[]), "created_at": user.get("created_at")}}

@router.post("/token/refresh")
async def refresh_token(request: Request, body: Optional[dict] = None):
    # Accept refresh token via body or HttpOnly cookie
    token = None
    if body and body.get("refresh_token"):
        token = body.get("refresh_token")
    else:
        token = request.cookies.get("refresh_token")

    payload = verify_token(token) if token else None
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not await db_manager.is_refresh_token_valid(user_id, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or not found")

    access_token = create_token({"sub": user_id}, token_type="access")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(request: Request, response: Response, body: Optional[dict] = None):
    # Accept refresh token via cookie or body
    token = None
    if body and body.get("refresh_token"):
        token = body.get("refresh_token")
    else:
        token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="refresh_token required")
    data = verify_token(token)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user_id = data.get("sub")
    jti = data.get("jti")
    await db_manager.revoke_refresh_token(user_id, jti)

    # Clear cookie
    response.delete_cookie("refresh_token")
    return {"detail": "Successfully logged out"}

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
