import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
import jwt
from jwt import (
    ExpiredSignatureError,
    InvalidTokenError
)

from app.config import settings

# ======================================================
# Logging
# ======================================================

logger = logging.getLogger(__name__)

# ======================================================
# Password Utilities
# ======================================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt directly.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    """
    Verify plain password against hash.
    """
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except Exception as e:
        logger.warning(
            f"Password verification failed: {e}"
        )
        return False


# ======================================================
# JWT Token Creation
# ======================================================

def create_token(
    data: Dict[str, Any],
    token_type: str = "access"
) -> str:
    """
    Create JWT token.

    Args:
        data: Payload dictionary.
        token_type: access | refresh

    Returns:
        Encoded JWT string.
    """

    if token_type not in ["access", "refresh"]:
        raise ValueError(
            "token_type must be 'access' or 'refresh'"
        )

    to_encode = data.copy()

    now = datetime.now(timezone.utc)

    if token_type == "access":
        expire = now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    else:
        expire = now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({
        "jti": str(uuid.uuid4()),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    })

    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


# ======================================================
# JWT Verification
# ======================================================

def verify_token(
    token: str
) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token.

    Returns:
        Payload if valid, otherwise None.
    """

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        required_fields = [
            "sub",
            "exp",
            "jti",
            "type"
        ]

        for field in required_fields:
            if field not in payload:
                logger.warning(
                    f"Missing JWT field: {field}"
                )
                return None

        return payload

    except ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None

    except InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None

    except Exception as e:
        logger.error(
            f"Unexpected JWT verification error: {e}"
        )
        return None


# ======================================================
# Optional Helper
# ======================================================

def is_token_expired(
    payload: Dict[str, Any]
) -> bool:
    """
    Check if token payload has expired.
    """

    exp = payload.get("exp")

    if not exp:
        return True

    current_time = int(
        datetime.now(timezone.utc).timestamp()
    )

    return current_time > exp