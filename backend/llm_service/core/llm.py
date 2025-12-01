import httpx
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from config import settings

# 1. 初始化模型
llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    model=settings.LLM_MODEL_NAME,
    temperature=0.1,  # 降低温度，让它更死板、更听话
    streaming=True
)

# 2. 这里的 Prompt 模板写得越严厉越好
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """你是一个“大模型应用开发”领域的专属智能客服。
你必须严格遵守以下规则：
1. 【绝对禁止】使用你预训练的通用知识回答。
2. 你只能根据下方的【检索知识】来回答问题。
3. 如果【检索知识】为空，或者与问题无关，你必须回答：“抱歉，知识库中没有相关内容。”
4. 请保持专业、简洁的语气。
5.你是一个“大模型应用开发”领域的专属智能客服

【检索知识】：
{context}"""),

    # 插入历史记录
    MessagesPlaceholder(variable_name="history"),

    ("human", "{question}"),
])


# 3. Redis History
def get_message_history(session_id: str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=settings.REDIS_URL,
        ttl=settings.SESSION_TTL
    )


async def search_knowledge_base(query: str):
    """
    调用 KB Service 获取相关知识
    """
    try:
        print(f"🔍 [DEBUG] 正在检索: {query}")  # 调试日志
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.KB_SERVICE_URL}/documents/search",
                json={"query": query, "top_k": 3},
                timeout=10.0,
                headers={"X-Internal-Key": settings.INTERNAL_API_KEY}
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                # 打印检索结果长度
                print(f"✅ [DEBUG] 检索成功，找到 {len(results)} 条文档")

                context = "\n\n".join([f"文档{i + 1}: {item['content']}" for i, item in enumerate(results)])
                return context if context else ""  # 如果没结果，返回空字符串
            else:
                print(f"❌ [DEBUG] KB Service 报错: {response.status_code} - {response.text}")
                return ""  # 出错时返回空，防止模型读到错误信息
    except Exception as e:
        print(f"❌ [DEBUG] 连接 KB Service 失败: {e}")
        return ""


async def rag_chat_stream(query: str, session_id: str):
    # 1. 检索
    context = await search_knowledge_base(query)

    # 🔥🔥🔥 关键调试：看看到底发给了模型什么上下文 🔥🔥🔥
    print(f"📝 [DEBUG] 最终 Context 内容:\n{context}")
    print("--------------------------------------------------")

    # 2. 构建 Chain
    chain = prompt_template | llm | StrOutputParser()

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_message_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    # 3. 流式调用
    async for chunk in chain_with_history.astream(
            {"question": query, "context": context},
            config={"configurable": {"session_id": session_id}}
    ):
        yield chunk