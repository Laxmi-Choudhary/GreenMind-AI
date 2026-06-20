import logging
from typing import Optional

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from app.database import db_manager
from app.utils.auth_utils import verify_token

# ======================================================
# Logging
# ======================================================

logger = logging.getLogger(__name__)

# ======================================================
# Security Scheme
# ======================================================

security = HTTPBearer(auto_error=True)

# Optional security (for public endpoints)
optional_security = HTTPBearer(auto_error=False)


# ======================================================
# Helper Function
# ======================================================

async def _get_user_from_token(token: str) -> Optional[dict]:
    """
    Validate token and return user.
    """

    payload = verify_token(token)

    if not payload:
        logger.warning("Invalid or expired token")
        return None

    if payload.get("type") != "access":
        logger.warning("Non-access token used")
        return None

    user_id = payload.get("sub")

    if not user_id:
        logger.warning("Token missing subject")
        return None

    user = await db_manager.get_user_by_id(user_id)

    if not user:
        logger.warning(f"User not found: {user_id}")
        return None

    return user


# ======================================================
# Required Authentication
# ======================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get authenticated user.
    Raises HTTP 401 if invalid.
    """

    token = credentials.credentials

    user = await _get_user_from_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


# ======================================================
# Optional Authentication
# ======================================================

async def get_optional_current_user(
    credentials: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(optional_security)
) -> Optional[dict]:
    """
    Returns authenticated user if token exists,
    otherwise returns None.
    """

    if not credentials:
        return None

    return await _get_user_from_token(
        credentials.credentials
    )


# ======================================================
# Admin Authorization (Optional Future Use)
# ======================================================

async def get_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Restrict endpoint access to admins only.
    Requires user document to contain:

    {
        "role": "admin"
    }
    """

    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user