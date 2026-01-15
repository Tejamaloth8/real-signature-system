from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.deps import get_db
from app.db.models import User
from app.core.security import hash_password, verify_password
from app.services.crypto_service import generate_keypair, create_access_token

router = APIRouter()

# ------------------------
# Schemas
# ------------------------
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ------------------------
# Register
# ------------------------
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(data.password)
    private_key, public_key = generate_keypair()

    user = User(
        email=data.email,
        password_hash=password_hash,
        private_key_enc=private_key,
        public_key=public_key,
        aes_key=b"temp_aes_key"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}

# ------------------------
# Login
# ------------------------
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}
