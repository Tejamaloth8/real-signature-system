from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey
)
from cryptography.hazmat.primitives import serialization

def generate_keypair():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_bytes, public_bytes

def sign_data(private_key_bytes: bytes, data: bytes) -> bytes:
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None
    )
    return private_key.sign(data)

def verify_signature(public_key_bytes: bytes, data: bytes, signature: bytes) -> bool:
    public_key = serialization.load_pem_public_key(public_key_bytes)
    try:
        public_key.verify(signature, data)
        return True
    except Exception:
        return False
