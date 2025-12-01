import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8000")
    KB_SERVICE_URL = os.getenv("KB_SERVICE_URL", "http://kb-service:8000")
    # 👇 新增 Auth Service 地址
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
    # 👇 新增 密钥 (必须与 Auth Service 一致)
    SECRET_KEY = os.getenv("SECRET_KEY", "unsafe_secret_key")
    ALGORITHM = "HS256"

settings = Config()