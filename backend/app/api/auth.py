"""
Authentication API Endpoints
"""

import re
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, Token, UserCreate, UserLogin, UserResponse
from app.auth import create_access_token, get_current_user, hash_password, verify_password

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

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Google-only accounts have no usable password
    if user.hashed_password == "!":
        raise HTTPException(status_code=401, detail="This account uses Google Sign-In")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/google", response_model=Token)
async def google_login(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Sign in or register via Google ID token"""
    # Verify the token with Google
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": data.id_token},
            timeout=10,
        )

    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    info = r.json()

    # Verify the token is for our app (skip check if GOOGLE_CLIENT_ID not configured)
    if settings.GOOGLE_CLIENT_ID and info.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Google token audience mismatch")

    google_id = info.get("sub")
    email = info.get("email", "")
    display_name = info.get("name") or email.split("@")[0]

    if not google_id:
        raise HTTPException(status_code=401, detail="Could not retrieve Google user ID")

    # 1. Try to find by google_id
    user = db.query(User).filter(User.google_id == google_id).first()

    # 2. Try to link to an existing account with the same email as username
    if not user and email:
        user = db.query(User).filter(User.username == email).first()
        if user:
            user.google_id = google_id
            db.commit()

    # 3. Create a new account
    if not user:
        base = re.sub(r"[^a-z0-9_]", "_", display_name.lower())[:20] or "user"
        username = base
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base}{counter}"
            counter += 1

        user = User(
            id=str(uuid.uuid4()),
            username=username,
            hashed_password="!",  # Unusable — bcrypt hashes always start with $2b$
            google_id=google_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user"""
    return current_user
