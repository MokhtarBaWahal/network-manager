"""
Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account"""
    if len(data.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = db.query(User).filter(User.username == data.username.strip()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        id=str(uuid.uuid4()),
        username=data.username.strip(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login and receive a JWT token"""
    user = db.query(User).filter(User.username == data.username.strip()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user"""
    return current_user
