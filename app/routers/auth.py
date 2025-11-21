from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from app.config import settings

router = APIRouter(tags=["authentication"])

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # For now, hardcode authentication
    if form_data.username != "testuser" or form_data.password != "testpass":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Hardcoded user_id=1 for testuser (temporary until proper user auth is implemented)
    access_token = create_access_token(data={"sub": form_data.username, "user_id": 1})
    return {"access_token": access_token, "token_type": "bearer"}
