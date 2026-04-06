# ZURU Melon 知识问答 Agent

基于 LangChain 的智能知识问答系统，能够自动判断问题类型并选择合适的回答方式：
- **公司相关问题** → RAG 检索知识库后生成答案
- **实时问题** → 联网搜索最新信息后生成答案（天气、新闻、股价等）
- **通用问题** → 直接调用大模型回答

## 技术栈

- **框架**: LangChain + FastAPI
- **LLM**: Kimi (Moonshot) / OpenAI
- **搜索**: 百度 AI 搜索 API (实时信息)
- **API**: FastAPI + Uvicorn

## 项目结构

```
agent_test/
├── knowledge_base/              # 知识库文档
│   ├── Company Policies.md
│   ├── Company Procedures & Guidelines.md
│   └── Coding Style.md
├── src/
│   ├── config.py                # 配置管理
│   ├── document_loader.py       # 文档加载
│   ├── router.py                # 问题类型路由判断（company/realtime/general）
│   ├── rag_chain.py             # RAG 链（公司问题）
│   ├── search_chain.py          # 搜索链（实时问题）
│   ├── llm_chain.py             # 通用 LLM 链
│   └── agent.py                 # 主 Agent
├── static/
│   └── index.html               # 网页界面
├── main.py                      # CLI 入口
├── api.py                       # FastAPI 服务
├── test_questions.py            # 批量测试
└── requirements.txt
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

**使用 Kimi（推荐）：**
```bash
export KIMI_API_KEY="your-kimi-api-key"
```

**或使用 OpenAI：**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

**百度 AI 搜索（用于实时问题）：**
```bash
export BAIDU_API_KEY="your-baidu-api-key"
```
获取地址：https://console.bce.baidu.com/ai-search/qianfan/ais/console/apiKey

或在项目根目录创建 `.env` 文件：

```
KIMI_API_KEY=your-kimi-api-key
BAIDU_API_KEY=your-baidu-api-key
```

### 3. 运行

**命令行交互：**
```bash
python main.py
```

**批量测试：**
```bash
python test_questions.py
```

## 使用示例

### 公司相关问题（走 RAG）

```
🤖 ZURU Melon 知识问答 Agent
==================================================

📝 你的问题: 公司的年假政策是什么？

🏢 [知识库] 回答：
----------------------------------------
根据公司政策，员工每年享有 20 天带薪年假...
----------------------------------------

📝 你的问题: Python 命名规范是什么？

🏢 [知识库] 回答：
----------------------------------------
根据编码规范：
- 变量和函数使用 snake_case
- 类名使用 PascalCase
- 常量使用 ALL_CAPS
----------------------------------------
```

### 实时问题（走搜索）

```
📝 你的问题: 今天天气怎么样？

🔍 [实时搜索] 回答：
----------------------------------------
根据实时搜索结果，今天...
----------------------------------------

📝 你的问题: 最新AI新闻

🔍 [实时搜索] 回答：
----------------------------------------
根据最新搜索结果...
----------------------------------------
```

### 通用问题（走 LLM）

```
📝 你的问题: 什么是机器学习？

🌐 [通用模型] 回答：
----------------------------------------
机器学习是人工智能的一个分支...
----------------------------------------
```

## 配置选项

通过环境变量自定义行为：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` | - | **必需** OpenAI API 密钥 |
| `LLM_MODEL` | gpt-3.5-turbo | 主 LLM 模型 |
| `CHUNK_SIZE` | 500 | 文档分块大小 |
| `CHUNK_OVERLAP` | 50 | 分块重叠大小 |
| `RETRIEVAL_TOP_K` | 3 | RAG 检索文档数 |

## 核心流程

```
用户问题
    ↓
Router (关键词 + LLM 判断)
    ├─ "company"  → RAG 链 → 知识库检索 → LLM 生成答案
    ├─ "realtime" → 搜索链 → DuckDuckGo 搜索 → LLM 生成答案
    └─ "general"  → 通用 LLM 链 → 直接生成答案
```

**自动识别特征：**
- **company**: 公司、政策、年假、编码规范、ZURU 等
- **realtime**: 今天、现在、最新、天气、股价、新闻、金价等
- **general**: 其他所有问题

## FastAPI 服务

### 启动 API 服务

**本地访问（仅本机）：**
```bash
python -m uvicorn api:app --reload
```

**局域网访问（其他电脑可访问）：**
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

### 查看本机 IP

```bash
# Mac/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# 或
hostname -I
```

### 访问方式

**本机访问：**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "公司的年假是多少天？"}'
```

**其他电脑访问（假设你的 IP 是 192.168.1.100）：**
```bash
curl -X POST "http://192.168.1.100:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "公司的年假是多少天？"}'
```

### 网页界面

启动服务后，浏览器打开：
- **本机**：http://localhost:8000
- **其他电脑**：http://你的IP:8000 (如 http://192.168.1.100:8000)

直接输入问题，点击"获取答案"即可。

服务启动后：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### API 端点

**1. 问答接口**

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "公司的年假有多少天？"}'
```

响应：
```json
{
  "question": "公司的年假有多少天？",
  "question_type": "company",
  "source": "rag",
  "answer": "根据公司政策..."
}
```

**2. 仅分类问题类型**

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"question": "Python 怎么写类？"}'
```

响应：
```json
{
  "question": "Python 怎么写类？",
  "question_type": "general"
}
```

### Python 调用示例

```python
import requests

# 提问
response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "公司的编码规范是什么？"}
)
result = response.json()
print(result["answer"])
```

## 扩展知识库

将新的 Markdown 文件放入 `knowledge_base/` 目录，重新运行即可自动加载新内容。

## 配置选项

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `KIMI_API_KEY` | - | Kimi API 密钥 |
| `OPENAI_API_KEY` | - | OpenAI API 密钥 |
| `LLM_MODEL` | moonshot-v1-8k | LLM 模型名 |
