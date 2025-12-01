from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os

# 1. 密码加密配置
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 2. JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # Token 有效期 1 天

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt