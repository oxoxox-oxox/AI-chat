这个路线图专为 **Python 全栈** 设计，采用"小步快跑"模式，每完成一个阶段都能看到切实可行的成果。

---

# 🗺️ Ollama AI 全栈项目长期修炼路线图 (Python 版)

## 🏷️ 项目总览

- **最终目标**：构建一个类似于 ChatGPT / Claude 的私有化 AI 智能助理网站。支持**多轮对话（带记忆）**、**流式打字机效果**、以及**本地知识库（RAG）**。
- **核心技术栈**：**Python + FastAPI (后端) + MySQL (数据库) + Vue (前端) + Ollama (AI 引擎)**
- **当前位置**：第一阶段已完成（FastAPI 后端 + Ollama 对话 + MySQL 存储），代码位于 `python_backend/` 目录。

---

## 📌 第一阶段：跑通管道 —— 后端与本地 AI 的第一次亲密接触 ✅

> **阶段目标**：搭建最基础的 FastAPI 后端，不考虑前端页面和数据库，纯粹让后端能够成功向 Ollama 发送请求并拿到回复。

### 1. 核心学习知识点

- **Python 异步编程**：
  - 理解 `async/await` 的运行机制（协程、事件循环）
  - 与 JS 的 `async/await` 语法相同但底层实现不同（asyncio vs libuv）

- **FastAPI 框架入门**：
  - 创建 HTTP 服务器：`uvicorn.run(app, host="0.0.0.0", port=3000)`
  - 数据校验：`Pydantic BaseModel` 替代 JS 的 JSON 解析
  - 路由声明：`@app.post("/api/chat")` 装饰器比 Express 更直观
  - 自动生成 API 文档：FastAPI 自带 Swagger UI（访问 `/docs`）

- **网络请求与异步编程**：
  - 使用 `httpx.AsyncClient` 向 Ollama API 发请求（Python 版 fetch）
  - Ollama `/api/chat` 请求体格式：`{ model: "...", messages: [...], stream: false }`
  - `/api/generate` 只支持单轮，多轮对话必须用 `/api/chat`

- **环境变量管理**：
  - `python-dotenv` 库（对应 JS 的 `dotenv`）
  - `os.getenv("KEY")` 读取

### 2. 成果复检清单

- [ ] 能够通过 `python main.py` 启动监听 3000 端口的服务器
- [ ] 用浏览器访问 `http://localhost:3000/docs` 看到自动生成的 API 文档
- [ ] 用 Postman 向 `http://localhost:3000/api/chat` 发送 POST 请求，能收到 AI 回复

---

## 📌 第二阶段：用户体验飞跃 —— 攻克"流式传输 (Streaming)"

> **阶段目标**：拒绝等待！让 AI 的回答像 ChatGPT 一样，一个字一个字地在前端"蹦"出来。

### 1. 核心学习知识点

- **Python 异步生成器 (Async Generator)**：
  - `async def` + `yield` 是实现 SSE 流式响应的核心语法
  - 对比 JS 的 `ReadableStream` + `getReader()`，FastAPI 的方式更简洁

- **FastAPI StreamingResponse**：
  - 返回 `StreamingResponse(generator(), media_type="text/event-stream")`
  - 不需要像 Express 那样手动设置 `Content-Type`、`Cache-Control` 等响应头
  - 但理解这些 HTTP 头的作用仍然重要：
    ```http
    Content-Type: text/event-stream
    Cache-Control: no-cache
    Connection: keep-alive
    ```

- **SSE (Server-Sent Events)**：
  - SSE vs WebSocket：SSE 是单向的（服务器→客户端），更简单，适合 AI 流式输出
  - SSE 数据格式：`data: <JSON>\n\n`（双换行是分隔符）
  - 结束标记：`data: [DONE]\n\n`

- **httpx 流式请求**：
  - `client.stream("POST", url, ...)` 逐行读取 Ollama 的 NDJSON 响应
  - `response.aiter_lines()` 异步迭代每一行

### 2. 成果复检清单

- [ ] 在浏览器中测试页面，数据分批逐字显示，不是一次性返回

---

## 📌 第三阶段：让 AI 拥有记忆 —— 数据库集成与多轮对话 ✅ (已完成)

> **阶段目标**：引入数据库，存储用户的聊天历史。让后端在每次提问时，自动把"历史记录"打包带给 Ollama，实现真正的"连续对话"。

### 1. 核心学习知识点

- **MySQL 关系型数据库**：
  - 关系型数据库（SQL）的基本概念：表、行、列、外键
  - 与 MongoDB（文档型）的区别：SQL 有固定的表结构、支持 JOIN
  - 本项目使用 MySQL 而非 MongoDB

- **mysql-connector-python**：
  - 连接池（Connection Pool）：为什么需要连接池、连接的生命周期
  - 参数化查询：`cursor.execute("... %s", (value,))` 防止 SQL 注入
  - dictionary cursor：`cursor(dictionary=True)` 返回字典而非元组

- **业务逻辑设计（Context 管理）**：
  - 当收到新问题时，根据 `sessionId` 查出最近的 20 条历史消息
  - 使用 `ORDER BY created_at ASC LIMIT 20` 控制上下文长度
  - 将 `[历史消息] + [当前新问题]` 组装成 Ollama 需要的 `messages` 数组
  - AI 结束响应后，将 AI 的完整回复持久化到 MySQL

- **数据库表设计**：
  ```sql
  sessions (id, title, created_at, updated_at)
  messages (id, session_id, role, content, created_at)
  -- role: 'user' | 'assistant'
  -- session_id 外键关联 sessions(id)，ON DELETE CASCADE
  ```

### 2. 成果复检清单

- [ ] 第一次提问："我叫小明"
- [ ] 第二次提问："我叫什么名字？"，AI 能够准确回答出"你叫小明"
- [ ] 检查 MySQL 数据库，确认 `sessions` 和 `messages` 表中正确存入了记录

---

## 📌 第四阶段：规范化与安全性 —— 变成真正的"后端工程师"

> **阶段目标**：代码不能只是"能跑"，还要安全和健壮。引入用户登录系统，保护你的 AI 算力不被别人盗用。

### 1. 核心学习知识点

- **用户认证与授权 (Auth)**：
  - 密码安全：使用 `bcrypt` 对用户密码进行哈希加密（Python 库：`bcrypt`）
  - **JWT (JSON Web Token)**：无状态认证机制
    - 登录成功后签发令牌：`python-jose` 库
    - 每次 AI 提问时在请求头携带：`Authorization: Bearer <token>`

- **FastAPI 中间件 / 依赖注入**：
  - 编写权限校验依赖（Depends），拦截未登录的请求
  - 与 Express 中间件的对比：FastAPI 用 `Depends(get_current_user)` 更灵活
  - **数据隔离逻辑**：确保用户 A 只能看到自己的聊天历史（查询时加 `WHERE userId = ?`）

- **SQLAlchemy ORM 引入（推荐此时迁移）**：
  - ORM 是什么：用 Python 类映射数据库表，免写 SQL
  - Session 和 Message 的 ORM 模型定义
  - 与原生 SQL 的对比：代码更简洁但需要学习 ORM 概念

- **健壮性防护**：
  - 全局异常处理器（`@app.exception_handler`）
  - 环境变量管理：数据库密码、JWT_SECRET 全部在 `.env`
  - 项目结构重构：拆分 `routers/`、`services/`、`models/`

### 2. 成果复检清单

- [ ] 没有登录（或 Token 过期）时，访问 AI 接口会收到 `401 Unauthorized`
- [ ] 用户 A 登录后，无法通过修改参数查看到用户 B 的聊天记录

---

## 📌 第五阶段（终极挑战）：知识库 RAG —— 向量检索与文档对话

> **阶段目标**：让 AI 能够基于你上传的本地文档（如本地的规则手册、小说等）进行精准回答。

### 1. 核心学习知识点

- **文本预处理与嵌入 (Embeddings)**：
  - 把大文档按字符数"切碎"成小文本段（Chunks，建议 500-1000 字符/chunk）
  - 调用 Ollama 的 `/api/embeddings` 接口，把文本转为高维向量
  - Python 文本处理：比 JS 更方便（原生 `re`、`textwrap`）

- **向量数据库**：
  - 向量相似度：余弦相似度概念
  - 推荐方案：**ChromaDB**（Python 原生支持，本地运行）
  - 核心操作：存向量 + 元数据 → 按相似度检索 Top-K

- **RAG 业务流控制**：
  ```
  用户提问 → Embedding(提问) → 向量库检索 Top-K 相关段落
  → 拼成 Prompt: "参考以下文档回答问题：\n[段落1]\n[段落2]\n\n问题：[用户提问]"
  → 发给 Ollama → 返回带引用的回答
  ```

### 2. 成果复检清单

- [ ] 上传一个文档后，问文档内的问题，AI 能引用原文准确回答
- [ ] 问文档外的问题，AI 不会胡乱编造（或明确表示不知道）

---

## 💡 给你的长期执行建议：

1. **不要急于求成**：每个阶段都足够你消化 1-2 周甚至更久
2. **善用 FastAPI 的 `/docs`**：FastAPI 自带 Swagger UI，可以直接在浏览器里测试所有 API
3. **先跑通再优化**：第一阶段不要纠结代码结构，路由全放 `main.py` 没问题；到第四阶段再重构拆分
4. **遇到卡壳怎么办**：Python 的报错通常很直白，学会看 Traceback。最容易卡壳的地方是 **异步生成器** 和 **数据库连接池配置**

你当前已完成第一/三阶段，可以直接从第二阶段（流式传输已实现）开始验收，然后进入第四阶段。
