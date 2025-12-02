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
<img width="3014" height="1654" alt="image" src="https://github.com/user-attachments/assets/c1aa25ff-15a1-4743-86b4-93308dc0fb0a" />

---

## 🏗️ 系统架构 (Architecture)

系统采用典型的微服务架构，通过 Docker Compose 进行编排。
<img width="1906" height="1434" alt="image" src="https://github.com/user-attachments/assets/9342379b-2236-432e-af47-3d42651751a6" />

## 🛠️ 技术栈 (Tech Stack)
## 技术架构
| 模块 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Vue 3, TypeScript, Element Plus | 现代化响应式 UI，Markdown 渲染 |
| 网关 | FastAPI, FastAPI-Limiter | 统一入口，负责鉴权、限流、路由分发 |
| 核心服务 | Python 3.12, LangChain | RAG 逻辑编排，Prompt Engineering |
| 数据存储 | MySQL 9.x, Redis, ChromaDB | 关系型数据、会话缓存、向量数据库 |
| 大模型 | OpenAI SDK (阿里云百炼) | 接入 Qwen-Plus 等先进 LLM |
| 监控 | Prometheus, Grafana, Jaeger | Metrics 指标监控与分布式链路追踪 |
| 运维 | Docker, GitHub Actions | 容器化部署与自动化 CI/CD |

## 🚀 快速开始 (Quick Start)

### 1. 环境准备
确保本地已安装：
  Docker Desktop
  Node.js (v18+) & npm

### 2. 克隆项目
* ** git clone [https://github.com/your-username/LLM-Dev-Assistant.git](https://github.com/AirLin-K70/LLM-Dev-Assistant.git)
* ** cd LLM-Dev-Assistant

### 3. 配置环境变量
复制 .env填入你的 API Key：

### 4. 启动微服务集群
使用 Docker Compose 一键启动后端所有服务（包括数据库和监控组件）：
docker-compose up -d --build
首次启动需要下载镜像，请耐心等待 3-5 分钟。

### 5. 启动前端
cd frontend
npm install
npm run dev
访问浏览器：http://localhost:5173 即可开始使用！

## 📂 目录结构 (Directory Structure)
```txt
LLM-Dev-Assistant/
├── backend/                 # 后端微服务代码
│   ├── gateway/             # API 网关
│   ├── auth_service/        # 认证中心
│   ├── llm_service/         # RAG 与对话核心
│   └── kb_service/          # 知识库管理
├── frontend/                # Vue 3 前端代码
├── config/                  # 监控组件配置 (Prometheus, Promtail)
├── data/                    # 数据库持久化目录
├── test/                   # 自动化测试脚本
├── docker-compose.yml       # 容器编排文件
└── .github/workflows/       # CI/CD 流水线配置
```

## 🛡️ 安全特性详情
### 1. 网关限流 (Rate Limiting):
  策略：每用户/IP 每分钟限制 10 次对话请求。
  实现：基于 fastapi-limiter 和 Redis 滑动窗口算法。

### 2. 零信任通信 (Zero Trust):
  策略：微服务之间（如 Gateway -> Auth）的调用必须携带 X-Internal-Key。
  效果：即使内网某个容器被攻破，攻击者也无法随意调用其他敏感服务。

### 3. 身份验证:
  使用 OAuth2 + JWT (JSON Web Tokens) 标准流程。
  密码采用 Argon2 强哈希算法存储。

## 📊 监控平台访问
### 项目启动后，你可以通过以下地址访问监控面板：
Grafana (可视化看板): http://localhost:3000 (默认账号/密码: admin/admin)

Prometheus (指标): http://localhost:9090

Jaeger (链路追踪): http://localhost:16686

## 📄 版权说明 (License)
### 本项目采用 MIT License 开源。








