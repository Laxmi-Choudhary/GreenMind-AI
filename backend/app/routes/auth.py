from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Response,
    Request
)

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)

from typing import List, Optional
from datetime import datetime
import logging
import re

from app.database import db_manager
from app.utils.auth_utils import (
    hash_password,
    verify_password,
    create_token,
    verify_token
)
from app.middleware.auth_middleware import (
    get_current_user
)

# ======================================================
# Logging
# ======================================================

logger = logging.getLogger(__name__)

# ======================================================
# Router
# ======================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# ======================================================
# Request Models
# ======================================================

class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):

        value = value.strip()

        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError(
                "Username can contain only letters, numbers and underscores"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        if len(value) < 8:
            raise ValueError(
                "Password must be at least 8 characters long"
            )

        if len(value) > 72:
            raise ValueError(
                "Password cannot exceed 72 characters"
            )

        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number"
            )

        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ======================================================
# Response Models
# ======================================================

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
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ======================================================
# Helper Functions
# ======================================================

def build_user_response(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "points": user.get("points", 0),
        "level": user.get("level", 1),
        "badges": user.get("badges", []),
        "created_at": user["created_at"]
    }


def set_refresh_cookie(
    response: Response,
    refresh_token: str
):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
        path="/"
    )


# ======================================================
# Register
# ======================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register User"
)
async def register(
    user_in: UserRegister,
    response: Response
):

    existing = await db_manager.get_user_by_email(
        user_in.email.lower()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_data = {
        "username": user_in.username.strip(),
        "email": user_in.email.lower(),
        "hashed_password": hash_password(
            user_in.password
        ),
        "points": 0,
        "level": 1,
        "badges": [],
        "created_at": datetime.utcnow().isoformat()
    }

    user = await db_manager.create_user(user_data)

    access_token = create_token(
        {"sub": user["id"]},
        token_type="access"
    )

    refresh_token = create_token(
        {"sub": user["id"]},
        token_type="refresh"
    )

    payload = verify_token(refresh_token)

    if payload:
        await db_manager.save_refresh_token(
            user["id"],
            payload.get("jti"),
            payload.get("exp")
        )

    set_refresh_cookie(
        response,
        refresh_token
    )

    logger.info(
        f"User registered: {user['email']}"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": build_user_response(user)
    }


# ======================================================
# Login
# ======================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login"
)
async def login(
    credentials: UserLogin,
    response: Response
):

    user = await db_manager.get_user_by_email(
        credentials.email.lower()
    )

    if not user or not verify_password(
        credentials.password,
        user.get("hashed_password")
    ):
        logger.warning(
            f"Failed login attempt: {credentials.email}"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_token(
        {"sub": user["id"]},
        token_type="access"
    )

    refresh_token = create_token(
        {"sub": user["id"]},
        token_type="refresh"
    )

    payload = verify_token(refresh_token)

    if payload:
        await db_manager.save_refresh_token(
            user["id"],
            payload.get("jti"),
            payload.get("exp")
        )

    set_refresh_cookie(
        response,
        refresh_token
    )

    logger.info(
        f"User logged in: {user['email']}"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": build_user_response(user)
    }


# ======================================================
# Refresh Access Token
# ======================================================

@router.post(
    "/token/refresh",
    response_model=RefreshResponse
)
async def refresh_access_token(
    request: Request,
    body: Optional[RefreshTokenRequest] = None
):

    token = (
        body.refresh_token
        if body else
        request.cookies.get("refresh_token")
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    jti = payload.get("jti")

    valid = await db_manager.is_refresh_token_valid(
        user_id,
        jti
    )

    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Refresh token revoked"
        )

    access_token = create_token(
        {"sub": user_id},
        token_type="access"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ======================================================
# Logout
# ======================================================

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    body: Optional[RefreshTokenRequest] = None
):

    token = (
        body.refresh_token
        if body else
        request.cookies.get("refresh_token")
    )

    if token:
        payload = verify_token(token)

        if payload:
            await db_manager.revoke_refresh_token(
                payload.get("sub"),
                payload.get("jti")
            )

    response.delete_cookie(
        key="refresh_token",
        path="/"
    )

    return {
        "detail": "Successfully logged out"
    }


# ======================================================
# Current User
# ======================================================

@router.get(
    "/me",
    response_model=UserResponse
)
async def get_me(
    current_user: dict = Depends(
        get_current_user
    )
):
    return build_user_response(
        current_user
    )