import os
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List

import uvicorn
from fastapi import Depends, HTTPException, status
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.auth import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash
)
from app.database import get_db
from app.dependencies import get_current_user, sanitize_input
from app.models import DataItem, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import engine, Base, SessionLocal
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(
                username="testuser",
                password_hash=get_password_hash("TestPassword123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("Test user created: testuser / TestPassword123")
        if not db.query(DataItem).filter_by(owner_id=user.id).first():
            item = DataItem(
                title="Test Data",
                description="<script>alert('XSS')</script>",
                owner_id=user.id
            )
            db.add(item)
            db.commit()
            print("Test data added to /api/data")
    finally:
        db.close()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Lab1",
    description="Лабораторная работа: Защищенное REST API с интеграцией в CI/CD",
    version="1.0.0"
)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class DataItemResponse(BaseModel):
    id: int
    title: str
    description: str

    model_config = ConfigDict(from_attributes=True)


@app.post("/auth/login", response_model=TokenResponse)
async def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/api/data", response_model=List[DataItemResponse])
async def get_data(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    items = db.query(DataItem).filter_by(owner_id=current_user.id).all()

    safe_items = []
    for item in items:
        safe_items.append({
            "id": item.id,
            "title": sanitize_input(item.title),
            "description": sanitize_input(item.description)
        })

    return safe_items


@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
