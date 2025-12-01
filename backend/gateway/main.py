from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from jose import JWTError, jwt
import httpx
import os
from config import settings
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# 读取内部密钥
INTERNAL_KEY = os.getenv("INTERNAL_API_KEY")


# ==========================================
# ⚡️ 生命周期管理 (修复报错的关键)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 启动时：连接 Redis 用于限流
    # 注意：在 Docker 网络中，主机名是 'redis'，端口 6379
    redis_connection = redis.from_url("redis://redis:6379/0", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    print("✅ Rate Limiter Initialized via Redis")

    yield  # 应用运行中...

    # 2. 关闭时：断开连接
    await redis_connection.close()


# 初始化 App，注入 lifespan
app = FastAPI(title="AI API Gateway", lifespan=lifespan)

# 自动通过 /metrics 接口暴露指标
Instrumentator().instrument(app).expose(app)

# 设置服务名称
resource = Resource(attributes={SERVICE_NAME: "gateway-service"})

provider = TracerProvider(resource=resource)

# 配置导出器 (发送到 Jaeger 容器的 4317 端口)
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

# 自动植入 FastAPI
FastAPIInstrumentor.instrument_app(app)

# 1. CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 认证逻辑
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username, "user_id": payload.get("user_id"), "role": payload.get("role", "user")}
    except JWTError:
        raise credentials_exception


# 简单的管理员权限检查
async def get_admin_user(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


@app.get("/")
def health_check():
    return {"status": "healthy", "service": "api-gateway"}


# ==========================================
# 3. 认证相关接口 (Auth Proxy)
# ==========================================

@app.post("/api/auth/register")
async def register_proxy(request: Request):
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.AUTH_SERVICE_URL}/register",
                json=body,
                headers={"X-Internal-Key": INTERNAL_KEY}
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/token")
async def login_proxy(request: Request):
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.AUTH_SERVICE_URL}/token",
                json=body,
                headers={"X-Internal-Key": INTERNAL_KEY}
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 4. 业务接口 (RESTful 路由 + 限流 + 零信任)
# ==========================================

# 转发聊天请求 (LLM Service)
# 🔥 限流策略：每 60 秒最多 10 次请求
@app.post("/api/conversations/chat", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def chat_proxy(request: Request, user: dict = Depends(get_current_user)):
    try:
        body = await request.json()
        body['user_id'] = user['username']

        async def proxy_stream():
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    req = client.build_request(
                        "POST",
                        f"{settings.LLM_SERVICE_URL}/conversations/chat",
                        json=body,
                        headers={"X-Internal-Key": INTERNAL_KEY}  # 零信任 Key
                    )
                    response = await client.send(req, stream=True)

                    if response.status_code != 200:
                        yield f"Error: {response.status_code}".encode()
                        return

                    async for chunk in response.aiter_bytes():
                        yield chunk
                except Exception as e:
                    yield f"Error: {str(e)}".encode()

        return StreamingResponse(proxy_stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 清空记忆接口
@app.delete("/api/conversations")
async def clear_history_proxy(user: dict = Depends(get_current_user)):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{settings.LLM_SERVICE_URL}/conversations/{user['username']}",
                headers={"X-Internal-Key": INTERNAL_KEY}
            )
            return JSONResponse(status_code=resp.status_code, content={})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 新增知识库文档接口 (RBAC: 仅管理员)
@app.post("/api/documents")
async def create_doc_proxy(request: Request, user: dict = Depends(get_admin_user)):
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.KB_SERVICE_URL}/documents",
                json=body,
                headers={"X-Internal-Key": INTERNAL_KEY}
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))