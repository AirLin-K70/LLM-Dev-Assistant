import json
import os
from langchain_core.documents import Document
from core.db import get_vector_store

# 数据文件路径
DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")


def ingest_data():
    print(f"🚀 开始加载数据: {DATA_PATH}")

    # 1. 读取 JSON
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 转换为 LangChain Document 对象
    documents = []
    for item in data:
        # 将 similar_questions 合并到 content 中，增加被召回的概率
        enhanced_content = f"{item['content']}\n\n相关问题参考:\n" + "\n".join(item['similar_questions'])

        doc = Document(
            page_content=enhanced_content,
            metadata={
                "id": item["id"],
                "category": item["category"],
                "topic": item["topic"],
                "source": item["source"]
            }
        )
        documents.append(doc)

    print(f"📄 解析完成，共 {len(documents)} 条文档。正在向量化并存入 Chroma...")

    # 3. 获取向量库连接
    vector_store = get_vector_store()

    # 4. 存入数据 (add_documents 会自动调用 OpenAI Embedding API)
    # ids 确保如果重复运行，可以通过 ID 去重或更新（取决于具体实现，Chroma通常需要手动处理去重，这里先简化直接添加）
    ids = [d.metadata["id"] for d in documents]
    vector_store.add_documents(documents=documents, ids=ids)

    print("✅ 数据入库成功！")


if __name__ == "__main__":
    ingest_data()