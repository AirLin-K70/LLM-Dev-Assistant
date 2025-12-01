from fastapi import FastAPI, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, engine
from models import Base, User
from utils import get_password_hash, verify_password, create_access_token
from fastapi.security import APIKeyHeader
import os
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# 自动创建表结构 (生产环境建议用 Alembic，这里简化)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

# 自动通过 /metrics 接口暴露指标
Instrumentator().instrument(app).expose(app)

# 设置服务名称
resource = Resource(attributes={SERVICE_NAME: "auth-service"})

provider = TracerProvider(resource=resource)

# 配置导出器 (发送到 Jaeger 容器的 4317 端口)
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

# 自动植入 FastAPI
FastAPIInstrumentor.instrument_app(app)

#零信任安全逻辑
INTERNAL_KEY = os.getenv("INTERNAL_API_KEY")
api_key_header = APIKeyHeader(name="X-Internal-Key", auto_error=False)

async def verify_internal_key(api_key: str = Security(api_key_header)):
    if api_key != INTERNAL_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auth Service: Internal access denied"
        )
    return api_key


# --- Pydantic 模型 (用于请求参数校验) ---
class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInfo(BaseModel):
    id: int
    username: str
    balance: float


# --- 接口 ---
@app.post("/register", response_model=UserInfo, dependencies=[Depends(verify_internal_key)])
def register(user: UserRegister, db: Session = Depends(get_db)):
    # 1. 检查用户是否存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 2. 创建新用户
    hashed_pwd = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pwd)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=Token, dependencies=[Depends(verify_internal_key)])
def login_for_access_token(user: UserLogin, db: Session = Depends(get_db)):
    # 1. 查用户
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 签发 Token (把用户ID和用户名存进 Token)
    access_token = create_access_token(data={"sub": db_user.username, "user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserInfo, dependencies=[Depends(verify_internal_key)])
def read_users_me(username: str, db: Session = Depends(get_db)):
    # 这个接口主要供 Gateway 验证 Token 后调用，获取最新余额
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 简单扣费接口 (供 Gateway/Billing 调用)
@app.post("/users/{user_id}/deduct", dependencies=[Depends(verify_internal_key)])
def deduct_balance(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.balance < amount:
        raise HTTPException(status_code=402, detail="Insufficient balance")  # 402 Payment Required

    user.balance -= amount
    db.commit()
    return {"status": "success", "new_balance": user.balance}