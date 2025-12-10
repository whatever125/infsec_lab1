import html

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.auth import verify_token
from app.database import get_db
from app.models import User

security = HTTPBearer()


def get_current_user(
        credentials=Depends(security),
        db=Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def sanitize_input(text: str) -> str:
    if text is None:
        return ""
    return html.escape(text)
