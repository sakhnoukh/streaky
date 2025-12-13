import hashlib
from passlib.context import CryptContext

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt (secure hashing for production)"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Supports both bcrypt (new) and SHA256 (legacy) for backward compatibility
    during migration. Old passwords will be automatically upgraded to bcrypt
    on next successful login.
    """
    # Try bcrypt first (new format)
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except (ValueError, TypeError):
        # Not a bcrypt hash, try legacy SHA256
        pass
    
    # Fallback to legacy SHA256 for backward compatibility
    legacy_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return legacy_hash == hashed_password
