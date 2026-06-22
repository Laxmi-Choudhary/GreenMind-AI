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
# Logging Configuration
# ======================================================

logger = logging.getLogger(__name__)

# ======================================================
# Security Schemes
# ======================================================

# Required authentication
security = HTTPBearer(
    auto_error=True
)

# Optional authentication
optional_security = HTTPBearer(
    auto_error=False
)

# ======================================================
# Internal Helper Function
# ======================================================

async def _get_user_from_token(
    token: str
) -> Optional[dict]:
    """
    Validate JWT token and return user.

    Returns:
        User dictionary if valid.
        None if invalid.
    """

    try:

        # Verify JWT token
        payload = verify_token(token)

        if not payload:

            logger.warning(
                "Invalid or expired token."
            )

            return None

        # Ensure access token only
        token_type = payload.get("type")

        if token_type != "access":

            logger.warning(
                f"Invalid token type: "
                f"{token_type}"
            )

            return None

        # Extract user ID
        user_id = payload.get("sub")

        if not user_id:

            logger.warning(
                "Token does not contain user ID."
            )

            return None

        # Fetch user from database
        user = await db_manager.get_user_by_id(
            user_id
        )

        if not user:

            logger.warning(
                f"User not found: {user_id}"
            )

            return None

        # Safety check for MongoDB ObjectId
        if "_id" in user:

            user["id"] = str(user["_id"])

            del user["_id"]

        return user

    except Exception as e:

        logger.exception(
            f"Authentication failed: {e}"
        )

        return None


# ======================================================
# Required Authentication Dependency
# ======================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials =
    Depends(security)
) -> dict:
    """
    Returns authenticated user.

    Raises:
        HTTPException 401 if invalid.
    """

    token = credentials.credentials

    user = await _get_user_from_token(
        token
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Invalid or expired "
                "authentication token"
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            }
        )

    return user


# ======================================================
# Optional Authentication Dependency
# ======================================================

async def get_optional_current_user(
    credentials: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(optional_security)
) -> Optional[dict]:
    """
    Return authenticated user if token exists.

    Otherwise return None.
    """

    if not credentials:

        return None

    return await _get_user_from_token(
        credentials.credentials
    )


# ======================================================
# Admin Authentication Dependency
# ======================================================

async def get_admin_user(
    current_user: dict =
    Depends(get_current_user)
) -> dict:
    """
    Allow only admin users.

    User document should contain:

    {
        "role": "admin"
    }
    """

    role = current_user.get(
        "role",
        "user"
    )

    if role.lower() != "admin":

        logger.warning(
            f"User {current_user.get('id')} "
            f"attempted admin access."
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Admin privileges required"
            )
        )

    return current_user


# ======================================================
# Request User Helper (Optional)
# ======================================================

async def get_request_user(
    request: Request
) -> Optional[dict]:
    """
    Helper function for middleware usage.

    Extracts Bearer token from request headers.
    """

    try:

        auth_header = request.headers.get(
            "Authorization"
        )

        if not auth_header:
            return None

        if not auth_header.startswith(
            "Bearer "
        ):
            return None

        token = auth_header.replace(
            "Bearer ",
            ""
        )

        return await _get_user_from_token(
            token
        )

    except Exception as e:

        logger.exception(
            f"Request user extraction failed: {e}"
        )

        return None