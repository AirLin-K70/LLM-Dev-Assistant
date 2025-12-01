# kb_service/core/db.py
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from .config import settings


def get_vector_store():
    """
    获取 LangChain 兼容的 Chroma 向量存储对象
    """
    # 1. 初始化 Embedding 模型 (关键修改点！)
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        model=settings.EMBEDDING_MODEL_NAME,
        check_embedding_ctx_length=False  # 阿里云有时候不需要这个检查，关闭以防报错
    )

    # 2. 连接到 Docker 中的 Chroma 服务
    client = chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT
    )

    # 3. 返回 LangChain 的 Chroma 包装器
    vector_store = Chroma(
        client=client,
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings,
    )

    return vector_store