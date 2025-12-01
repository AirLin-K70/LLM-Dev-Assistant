# 🚀 LLM-Dev-Assistant | 垂直领域大模型智能客服

<div align="center">

![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Vue](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)

<p align="center">
  <strong>基于 RAG (检索增强生成) 的企业级微服务 AI 问答系统</strong>
</p>

[✨ 在线演示 (Demo)](#) · [📖 接口文档](#) · [🐛 报告 Bug](../../issues)

</div>

---

## 📖 项目简介 (Introduction)

**LLM-Dev-Assistant** 是一个前后端分离、基于微服务架构的垂直领域智能客服系统。它不仅仅是一个简单的聊天机器人，而是一个**完全工程化**的 AI 解决方案。

本项目实现了从数据入库、向量检索、大模型生成到前端流式展示的完整闭环，并集成了**零信任安全策略**、**全链路可观测性 (Observability)** 以及 **CI/CD 流水线**，旨在模拟真实的生产环境 AI 应用开发标准。

### 🔥 核心亮点

* **🧠 RAG 知识引擎**: 基于 LangChain + ChromaDB，支持私有数据的高精度检索与问答。
* **💬 智能多轮对话**: 利用 Redis 实现带 TTL (过期时间) 的会话记忆，支持上下文理解。
* **⚡ 全链路流式响应**: 基于 SSE (Server-Sent Events) 技术，复刻 ChatGPT 的打字机体验。
* **🛡️ 企业级安全**:
    * **Zero Trust (零信任)**: 服务间通信强制校验内部密钥 (Internal API Key)。
    * **Rate Limiting**: 基于 Redis 的网关层限流，防止恶意刷接口。
    * **RBAC**: 完善的用户认证与基于角色的权限控制。
* **📊 全链路可观测性**: 集成 **Prometheus** (指标)、**Grafana** (可视化)、**Jaeger** (分布式追踪)，实时监控系统健康。
* **🔄 DevOps**: 配置 **GitHub Actions** 自动化 CI/CD 流水线，实现自动化测试与构建。

---

## 📸 系统预览 (Screenshots)

### 1. 智能对话界面
> 支持 Markdown 渲染、流式输出、历史记录自动滚动。
<img width="2392" height="1406" alt="image" src="https://github.com/user-attachments/assets/7fdbe6df-e662-4fab-8314-7ae214e58cd3" />



### 2. Grafana 监控大屏
> 实时展示 QPS、P99 延迟、服务错误率及 Docker 容器日志。
<img width="2362" height="1400" alt="image" src="https://github.com/user-attachments/assets/6eb2cd4a-9c36-49e0-af3f-b85f766b9879" />


---

## 🏗️ 系统架构 (Architecture)

系统采用典型的微服务架构，通过 Docker Compose 进行编排。

```mermaid
graph TD
    User[用户 (Browser)] -->|HTTP/WebSocket| Frontend[前端 (Vue 3 + TS)]
    Frontend -->|RESTful API| Gateway[API 网关 (FastAPI)]
    
    subgraph "可观测性 (Observability)"
        Prometheus --> Gateway & Services
        Jaeger --> Gateway & Services
        Grafana --> Prometheus & Jaeger
    end

    subgraph "后端微服务集群 (Docker Network)"
        Gateway -->|鉴权 & 限流| Auth[认证服务]
        Gateway -->|流式转发| LLM[大模型服务]
        Gateway -->|管理转发| KB[知识库服务]
        
        LLM -->|RAG 检索| KB
        LLM -->|会话记忆| Redis[(Redis 缓存)]
        
        Auth -->|读写用户| MySQL[(MySQL 8.0)]
        KB -->|向量检索| Chroma[(ChromaDB)]
    end

