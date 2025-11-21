import hashlib

def get_password_hash(password: str) -> str:
    """Hash a password using SHA256 (simple hashing for demo)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return get_password_hash(plain_password) == hashed_password
