from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------
# Password utils
# ---------------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# ---------------------------
# Token creation
# ---------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.auth.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.auth.refresh_token_expire_days))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.auth.refresh_secret_key, algorithm=settings.auth.algorithm)

# ---------------------------
# Token decoding
# ---------------------------
def decode_token(token: str):
    try:
        return jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
    except:
        return None

def decode_refresh_token(token: str):
    try:
        return jwt.decode(token, settings.auth.refresh_secret_key, algorithms=[settings.auth.algorithm])
    except:
        return None
