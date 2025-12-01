from fastapi import FastAPI, HTTPException, status, Path, Depends, Security
from pydantic import BaseModel, Field
from typing import List, Optional
from core.db import get_vector_store
from langchain_core.documents import Document
from fastapi.security import APIKeyHeader
import os
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

app = FastAPI(title="Knowledge Base Service")

# 自动通过 /metrics 接口暴露指标
Instrumentator().instrument(app).expose(app)

# 设置服务名称
resource = Resource(attributes={SERVICE_NAME: "kb-service"})

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
            detail="KB Service: Internal access denied (Wrong Key)"
        )
    return api_key


# --- 数据模型 ---
class KnowledgeDoc(BaseModel):
    id: str = Field(..., description="文档唯一ID")
    content: str = Field(..., description="知识内容")
    category: Optional[str] = "General"
    source: Optional[str] = "User Upload"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


# --- RESTful 接口 ---
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# 1. 新增知识 (Create)
@app.post("/documents", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_internal_key)])
def create_document(doc: KnowledgeDoc):
    try:
        vector_store = get_vector_store()

        # 转换为 LangChain Document
        new_doc = Document(
            page_content=doc.content,
            metadata={
                "id": doc.id,
                "category": doc.category,
                "source": doc.source
            }
        )

        # 存入 Chroma
        vector_store.add_documents(documents=[new_doc], ids=[doc.id])
        return {"message": "Document created successfully", "id": doc.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. 删除知识 (Delete)
@app.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_internal_key)])
def delete_document(doc_id: str = Path(...)):
    try:
        vector_store = get_vector_store()
        # Chroma 的 delete 方法
        vector_store.delete(ids=[doc_id])
        return  # 204 不返回内容
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. 检索知识 (Search - 通常用 POST 因为查询参数可能很长)
@app.post("/documents/search", dependencies=[Depends(verify_internal_key)])
def search_documents(request: SearchRequest):
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search_with_score(request.query, k=request.top_k)

        response = []
        for doc, score in results:
            response.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
        return {"results": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))