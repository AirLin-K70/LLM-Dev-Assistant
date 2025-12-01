import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen-plus")
    KB_SERVICE_URL = os.getenv("KB_SERVICE_URL", "http://kb-service:8000")
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SESSION_TTL = int(os.getenv("SESSION_TTL", 3600))
    INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")


settings = Config()