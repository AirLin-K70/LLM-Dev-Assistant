from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 构建 MySQL 连接字符串
# 格式: mysql+pymysql://user:password@host:port/db_name
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()