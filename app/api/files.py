from fastapi import APIRouter

router = APIRouter()

@router.post("/upload")
def upload_file(...):
    ...

@router.post("/sign/{doc_id}")
def sign_document(...):
    ...

@router.get("/verify/{doc_id}")
def verify_document(...):
    ...
