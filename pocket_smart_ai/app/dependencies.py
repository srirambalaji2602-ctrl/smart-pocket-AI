import jwt

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .database import get_db
from .models.db_models import User
from .services.auth_service import decode_access_token


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required",
        )

    try:
        payload = decode_access_token(token)

        user_id = int(payload["sub"])

    except (
        jwt.InvalidTokenError,
        KeyError,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user