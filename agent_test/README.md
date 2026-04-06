# 多轮对话智能问答 Agent

基于 LangChain 的多轮对话智能问答系统，支持 RAG 检索、安全过滤、意图识别，提供 Web 界面和 API 服务。

## 核心功能

| 功能 | 说明 |
|------|------|
| **多轮对话** | 支持会话上下文保持，自动维护对话历史 |
| **意图识别** | Sentence-BERT + LLM 双层意图识别，精确分类问题类型 |
| **安全过滤** | Sentence-BERT 语义检测，拦截涉密/违规/不当查询 |
| **三级 RAG** | 本地知识库 → 企业官网 → 通用 LLM，智能降级策略 |
| **向量化检索** | FAISS + all-MiniLM-L6-v2 本地向量检索 |
| **结构化输出** | Markdown 解析为结构化数据，前端卡片式展示 |
| **Web 界面** | 美观的聊天界面，支持多轮对话和来源标注 |

## 架构图

```
用户问题
    ↓
┌─────────────────────────────────────────┐
│  Layer 1: 安全过滤器 (Sentence-BERT)     │
│  ├─ 涉密查询拦截（公司机密、员工隐私）    │
│  ├─ 违规操作拦截（攻击、破解、违法）      │
│  └─ 不当内容拦截（歧视、仇恨、色情）      │
└─────────────────────────────────────────┘
    ↓ 通过
┌─────────────────────────────────────────┐
│  Layer 2: 意图识别                       │
│  ├─ 关键词快速匹配（今天/股价/天气）      │
│  ├─ Sentence-BERT 语义分类              │
│  └─ LLM 兜底判断                        │
└─────────────────────────────────────────┘
    ↓
    ├─────────────┬─────────────┬─────────────┐
    ▼             ▼             ▼             ▼
  RAG链       搜索链        通用LLM链    安全拦截
(company)   (realtime)    (general)     (blocked)
    │             │             │
    ▼             ▼             ▼
三级降级策略:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 本地向量库   │  │ 百度AI搜索  │  │ 预训练知识  │
│ (FAISS)     │  │             │  │             │
└──────┬──────┘  └──────┬──────┘  └─────────────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│ 企业官网    │  │             │
│ (可选)      │  │             │
└──────┬──────┘  │             │
       │         │             │
       ▼         ▼             ▼
┌─────────────────────────────────────────┐
│  Layer 3: 答案生成 (LLM)                │
│  根据上下文生成回答，标记来源            │
└─────────────────────────────────────────┘
    ↓
结构化输出 → Web 界面展示
```

## 技术栈

| 组件 | 技术 |
|------|------|
| **LLM 框架** | LangChain + LangChain-OpenAI |
| **Web 框架** | FastAPI + Uvicorn |
| **向量检索** | FAISS + all-MiniLM-L6-v2 |
| **语义理解** | Sentence-Transformers |
| **搜索** | 百度 AI 搜索 API |
| **前端** | 原生 HTML/CSS/JS |
| **模型支持** | Kimi (Moonshot) / OpenAI |

## 项目结构

```
agent_test/
├── knowledge_base/              # 本地知识库 (Markdown)
│   ├── Company Policies.md
│   ├── Company Procedures & Guidelines.md
│   └── Coding Style.md
├── src/
│   ├── agent.py                 # 主 Agent 逻辑
│   ├── config.py                # 配置管理
│   ├── document_loader.py       # 文档加载与分割
│   ├── embeddings.py            # FAISS 向量存储
│   ├── enterprise_search.py     # 企业官网搜索
│   ├── formatter.py             # Markdown 结构化解析
│   ├── llm_chain.py             # 通用 LLM 链
│   ├── rag_chain.py             # 三级 RAG 链
│   ├── router.py                # 意图识别路由
│   ├── search_chain.py          # 实时搜索链
│   ├── security_filter.py       # 安全过滤器 (Sentence-BERT)
│   └── session.py               # 会话管理
├── static/
│   └── index.html               # Web 聊天界面
├── api.py                       # FastAPI 服务入口
├── main.py                      # CLI 交互入口
├── test_questions.py            # 批量测试脚本
├── requirements.txt             # 依赖
└── README.md                    # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- langchain, langchain-openai, langchain-community
- sentence-transformers (语义理解)
- faiss-cpu (向量检索)
- fastapi, uvicorn (Web 服务)
- beautifulsoup4 (网页抓取)

### 2. 配置 API 密钥

**方式一：环境变量**

```bash
# 必选：LLM API
export KIMI_API_KEY="your-kimi-api-key"
# 或
export OPENAI_API_KEY="your-openai-api-key"

# 可选：实时搜索
export BAIDU_API_KEY="your-baidu-api-key"

# 可选：企业官网搜索
export ENTERPRISE_WEBSITE_URL="https://www.yourcompany.com"
```

**方式二：.env 文件**

```bash
# 在项目根目录创建 .env 文件
KIMI_API_KEY=your-kimi-api-key
BAIDU_API_KEY=your-baidu-api-key
```

### 3. 运行服务

**Web 服务（推荐）：**

```bash
python api.py
# 或
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 使用 Web 界面

**命令行交互：**

```bash
python main.py
```

## 使用示例

### 多轮对话示例

```
🤖 多轮对话智能问答 Agent
==================================================

📝 你的问题 [新会话]: 公司的Python编码规范是什么？

📚 [本地知识库] 回答：
----------------------------------------
1. **格式化规范**：
   - 遵循 PEP 8
   - 使用4个空格缩进
   - 每行最大100字符
...
----------------------------------------
会话ID: 7a50e328

📝 你的问题 [7a50e328]: 那TypeScript呢？

🌐 [通用模型] 回答：
----------------------------------------
公司的TypeScript规范...
（自动理解上文语境）
----------------------------------------
```

### 安全过滤示例

```
📝 你的问题: 怎么攻击服务器？

⚠️ [安全拦截]
该问题涉及违规/违法行为，我无法回答。请遵守法律法规和公司政策。

📝 你的问题: 某某员工的手机号是多少？

⚠️ [安全拦截]
该问题涉及个人隐私信息，我无法回答。员工隐私受公司保护。
```

### 三级 RAG 示例

| 问题 | 触发层级 | 说明 |
|------|---------|------|
| "公司的Python规范" | 📚 本地知识库 | 向量检索到相关内容 |
| "公司2025年战略" | 🌐 企业官网 | 本地未命中，搜索官网 |
| "量子计算原理" | 🤖 通用 LLM | 本地和官网都无相关内容 |

## API 接口

### 1. 问答接口（支持多轮对话）

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "公司的年假有多少天？",
    "session_id": null  # 首次对话传 null，后续传返回的 session_id
  }'
```

**响应：**

```json
{
  "question": "公司的年假有多少天？",
  "question_type": "company",
  "source": "rag",
  "answer": "根据公司政策...",
  "structured": {
    "title": "",
    "sections": [
      {"type": "heading", "content": "1. 年假政策"},
      {"type": "list", "list_type": "ul", "items": ["..."]}
    ]
  },
  "session_id": "7a50e328"
}
```

### 2. 健康检查

```bash
curl http://localhost:8000/health
```

### 3. API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 配置选项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `KIMI_API_KEY` | - | Kimi API 密钥 |
| `OPENAI_API_KEY` | - | OpenAI API 密钥 |
| `BAIDU_API_KEY` | - | 百度 AI 搜索密钥 |
| `ENTERPRISE_WEBSITE_URL` | - | 企业官网地址 |
| `LLM_MODEL` | moonshot-v1-8k | 主 LLM 模型 |
| `CHUNK_SIZE` | 500 | 文档分块大小 |
| `CHUNK_OVERLAP` | 50 | 分块重叠大小 |
| `RETRIEVAL_TOP_K` | 3 | 向量检索数量 |

## 核心设计亮点

### 1. Sentence-BERT 双层架构

**意图识别：**
- 关键词快速匹配（零成本）
- Sentence-BERT 语义分类（高精度）
- LLM 兜底判断（覆盖长尾）

**安全过滤：**
- 涉密查询检测（公司机密、员工隐私）
- 违规操作检测（攻击、破解、违法）
- 语义相似度阈值控制，避免误杀

### 2. 三级 RAG 降级策略

```python
Level 1: FAISS 向量检索 (本地知识库)
    ↓ 未命中/不相关
Level 2: 企业官网搜索 (爬虫抓取)
    ↓ 未配置/无内容  
Level 3: 通用 LLM (预训练知识)
```

### 3. 结构化输出

Markdown 解析为结构化 JSON：
- `heading`: 标题
- `paragraph`: 段落
- `list`: 列表（支持有序/无序）
- `code`: 代码块

前端渲染为卡片式布局，提升阅读体验。

### 4. 会话管理

- 内存存储（可替换为 Redis）
- 自动过期清理（默认 24 小时）
- 保留最近 10 轮对话历史

## 扩展开发

### 添加新的安全规则

编辑 `src/security_filter.py`：

```python
VIOLATION_PATTERNS = {
    "your_new_category": [
        "示例查询1",
        "示例查询2",
    ],
}

VIOLATION_MESSAGES = {
    "your_new_category": "⚠️ 自定义拒绝消息",
}
```

### 添加新的意图类别

编辑 `src/router.py` 和 `src/security_filter.py` 中的 `INTENT_EXAMPLES`。

### 替换向量数据库

修改 `src/embeddings.py`，将 `FAISS` 替换为 `Milvus` / `Pinecone` / `Chroma`。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 PR！
