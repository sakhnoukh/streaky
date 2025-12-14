import hashlib
import bcrypt

# Bcrypt has a 72-byte limit for passwords
BCRYPT_MAX_PASSWORD_LENGTH = 72


def _truncate_password(password: str) -> bytes:
    """Truncate password to 72 bytes for bcrypt compatibility."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_LENGTH:
        password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_LENGTH]
    return password_bytes


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt (secure hashing for production)
    
    Bcrypt has a 72-byte limit, so we truncate longer passwords.
    """
    password_bytes = _truncate_password(password)
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Supports both bcrypt (new) and SHA256 (legacy) for backward compatibility
    during migration. Old passwords will be automatically upgraded to bcrypt
    on next successful login.
    """
    # Try bcrypt first (new format)
    # Bcrypt hashes start with $2a$, $2b$, or $2y$
    if hashed_password.startswith('$2'):
        try:
            password_bytes = _truncate_password(plain_password)
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except (ValueError, TypeError):
            # Not a valid bcrypt hash, try legacy SHA256
            pass
    
    # Fallback to legacy SHA256 for backward compatibility
    legacy_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return legacy_hash == hashed_password
