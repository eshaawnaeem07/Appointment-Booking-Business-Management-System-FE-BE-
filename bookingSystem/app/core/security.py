from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import (
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_EXPIRE_DAYS
)
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise Exception(f"Password hashing failed: {str(e)}")


def verify_password(password: str, hashed: str):
    try:
        return pwd_context.verify(password, hashed)
    except Exception as e:
        raise Exception(f"Password verification failed: {str(e)}")


def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise Exception(f"Token creation failed: {str(e)}")

def create_refresh_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise Exception(f"Refresh token creation failed: {str(e)}")

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")

def generate_refresh_token():
    return secrets.token_hex(8)  # short like: a8f3k2p9x1

def verify_refresh_token(db, token: str):
    from app.models.user import User
    from datetime import datetime

    user = db.query(User).filter(User.refresh_token == token).first()

    if not user:
        raise Exception("Invalid refresh token")

    if not user.refresh_token_expiry or user.refresh_token_expiry < datetime.utcnow():
        raise Exception("Refresh token expired")

    return user