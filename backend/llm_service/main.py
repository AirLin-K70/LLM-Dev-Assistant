from fastapi import FastAPI, HTTPException, Path, status,Security,Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.llm import rag_chat_stream
from langchain_community.chat_message_histories import RedisChatMessageHistory
from config import settings
from fastapi.security import APIKeyHeader
import os
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

INTERNAL_KEY = os.getenv("INTERNAL_API_KEY")
api_key_header = APIKeyHeader(name="X-Internal-Key", auto_error=False)

async def verify_internal_key(api_key: str = Security(api_key_header)):
    if api_key != INTERNAL_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Internal service access denied"
        )
    return api_key

app = FastAPI(title="LLM Service")

# 自动通过 /metrics 接口暴露指标
Instrumentator().instrument(app).expose(app)

# 设置服务名称
resource = Resource(attributes={SERVICE_NAME: "llm-service"})

provider = TracerProvider(resource=resource)

# 配置导出器 (发送到 Jaeger 容器的 4317 端口)
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

# 自动植入 FastAPI
FastAPIInstrumentor.instrument_app(app)

class ChatRequest(BaseModel):
    query: str
    user_id: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 1. 对话资源 (Chat) - 依然是流式
@app.post("/conversations/chat", dependencies=[Depends(verify_internal_key)])
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        rag_chat_stream(request.query, session_id=request.user_id),
        media_type="text/event-stream"
    )

# 2. 清空记忆 (Delete History)
@app.delete("/conversations/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_conversation_history(user_id: str = Path(..., description="用户ID")):
    try:
        # 直接操作 Redis History 对象来清空
        history = RedisChatMessageHistory(
            session_id=user_id,
            url=settings.REDIS_URL
        )
        history.clear()
        return # 204
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))