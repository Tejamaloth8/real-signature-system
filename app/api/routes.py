from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.db.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.auth import get_current_user
from app.services.crypto_service import generate_keypair
from app.services.file_crypto import generate_aes_key, encrypt_file, decrypt_file
from app.services.heisenberg_service import (
    generate_keys,
    sign as h_sign,
    verify as h_verify,
    HeisenbergElement
)
from app.services.crypto_service import sign_data, verify_signature
from app.db.models import Document, Signature
import os, uuid, hashlib
from pydantic import BaseModel

router = APIRouter()

STORAGE_PATH = "storage"
os.makedirs(STORAGE_PATH, exist_ok=True)

# ------------------------
# Request Schemas
# ------------------------
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@router.get("/")
def root():
    return {"status": "running", "message": "Auth system active"}


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

    aes_key = generate_aes_key()

    user = User(
        email=data.email,
        password_hash=password_hash,
        public_key=public_key,
        private_key_enc=private_key,  # encrypted later (next step)
        aes_key=aes_key
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/protected")
def protected(user_email: str = Depends(get_current_user)):
    return {"message": f"Welcome {user_email}, you are authenticated"}


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_email).first()

    raw_data = file.file.read()
    encrypted_data = encrypt_file(raw_data, user.aes_key)

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(STORAGE_PATH, unique_name)

    with open(file_path, "wb") as f:
        f.write(encrypted_data)

    document = Document(
        filename=file.filename,
        filepath=file_path,
        owner_id=user.id
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "File uploaded & encrypted successfully",
        "document_id": document.id
    }


@router.get("/download/{document_id}")
def download_file(
    document_id: int,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_email).first()

    document = db.query(Document).filter(Document.id == document_id, Document.owner_id == user.id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    with open(document.filepath, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file(encrypted_data, user.aes_key)

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document.filename)[1]) as temp_file:
        temp_file.write(decrypted_data)
        temp_path = temp_file.name

    return FileResponse(temp_path, filename=document.filename, media_type='application/octet-stream')


@router.post("/sign/{doc_id}")
def sign_document(
    doc_id: int,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_email).first()
    document = db.query(Document).filter(Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    with open(document.filepath, "rb") as f:
        encrypted_data = f.read()

    doc_hash = hashlib.sha256(encrypted_data).digest()

    # ---- Ed25519 (REAL SIGNATURE) ----
    ed_signature = sign_data(user.private_key_enc, doc_hash)

    # ---- Heisenberg (RESEARCH SIGNATURE) ----
    g, h_private, h_public = generate_keys()
    r, z = h_sign(doc_hash, g, h_private)

    signature = Signature(
        document_id=document.id,
        signer_id=user.id,
        signature=ed_signature,
        heisenberg_r=f"{r.a},{r.b},{r.c}",
        heisenberg_z=str(z)
    )

    db.add(signature)
    db.commit()

    return {
        "message": "Document signed successfully",
        "ed25519": "stored",
        "heisenberg": "stored"
    }


@router.get("/verify/{doc_id}")
def verify_document(
    doc_id: int,
    db: Session = Depends(get_db)
):
    signature = db.query(Signature).filter(
        Signature.document_id == doc_id
    ).order_by(Signature.id.desc()).first()

    if not signature:
        raise HTTPException(status_code=404, detail="No signature found")

    document = db.query(Document).filter(Document.id == doc_id).first()

    with open(document.filepath, "rb") as f:
        encrypted_data = f.read()

    doc_hash = hashlib.sha256(encrypted_data).digest()

    # ---- Verify Ed25519 ----
    ed_valid = verify_signature(
        signature.signer.public_key,
        doc_hash,
        signature.signature
    )

    # ---- Verify Heisenberg ----
    r = HeisenbergElement.deserialize(signature.heisenberg_r)
    z = int(signature.heisenberg_z)

    g, _, h_public = generate_keys()  # demo public key
    h_valid = h_verify(doc_hash, g, h_public, (r, z))

    return {
        "ed25519_valid": ed_valid,
        "heisenberg_valid": h_valid
    }
