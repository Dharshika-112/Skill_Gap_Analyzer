"""Security helpers: password hashing and JWT tokens"""
import hashlib
import hmac
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from .config import MONGODB_DB_NAME, SECRET_KEY as DEFAULT_SECRET, MONGODB_URL
import os

from .database import get_collection

# JWT settings
SECRET_KEY = os.getenv('SECRET_KEY', DEFAULT_SECRET)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = SECRET_KEY.encode('utf-8')
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hmac.compare_digest(hash_password(plain), hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise

def get_user_by_email(email: str):
    users = get_collection('users')
    return users.find_one({"email": email})
