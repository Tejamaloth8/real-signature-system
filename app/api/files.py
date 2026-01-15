from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os, uuid, hashlib, tempfile

from app.db.deps import get_db
from app.db.models import User, Document, Signature
from app.core.auth import get_current_user
from app.services.file_crypto import encrypt_file, decrypt_file
from app.services.crypto_service import sign_data, verify_signature
from app.services.heisenberg_service import (
    generate_keys,
    sign as h_sign,
    verify as h_verify,
    HeisenbergElement
)

router = APIRouter()

STORAGE_PATH = "storage"
os.makedirs(STORAGE_PATH, exist_ok=True)

# ------------------------
# Upload
# ------------------------
@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

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
        "message": "File uploaded successfully",
        "document_id": document.id
    }

# ------------------------
# Sign
# ------------------------
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

    ed_signature = sign_data(user.private_key_enc, doc_hash)

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

    return {"message": "Document signed successfully"}

# ------------------------
# Verify
# ------------------------
@router.get("/verify/{doc_id}")
def verify_document(doc_id: int, db: Session = Depends(get_db)):
    signature = (
        db.query(Signature)
        .filter(Signature.document_id == doc_id)
        .order_by(Signature.id.desc())
        .first()
    )

    if not signature:
        raise HTTPException(status_code=404, detail="No signature found")

    document = db.query(Document).filter(Document.id == doc_id).first()

    with open(document.filepath, "rb") as f:
        encrypted_data = f.read()

    doc_hash = hashlib.sha256(encrypted_data).digest()

    ed_valid = verify_signature(
        signature.signer.public_key,
        doc_hash,
        signature.signature
    )

    r = HeisenbergElement.deserialize(signature.heisenberg_r)
    z = int(signature.heisenberg_z)

    g, _, h_public = generate_keys()
    h_valid = h_verify(doc_hash, g, h_public, (r, z))

    return {
        "ed25519_valid": ed_valid,
        "heisenberg_valid": h_valid
    }

