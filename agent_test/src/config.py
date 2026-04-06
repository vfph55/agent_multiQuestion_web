"""配置管理模块."""

import os
from pathlib import Path

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 知识库目录
KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"

# 向量存储目录
VECTOR_STORE_DIR = ROOT_DIR / "vector_store"
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KIMI_API_KEY = os.getenv("KIMI_API_KEY")

# 默认 Kimi API Key（如果不设置环境变量则使用此默认值）
DEFAULT_KIMI_API_KEY = "sk-ggJmGVQqRpSIIlNxojXNjmsq3MoWlnFo2OGiuCiLAFddm7gS"

# 确定使用哪个 API
# 优先级：环境变量 > 默认值
if KIMI_API_KEY:
    USE_KIMI = True
    API_KEY = KIMI_API_KEY
    BASE_URL = "https://api.moonshot.cn/v1"
elif OPENAI_API_KEY:
    USE_KIMI = False
    API_KEY = OPENAI_API_KEY
    BASE_URL = None
elif DEFAULT_KIMI_API_KEY:
    # 使用默认 Kimi Key
    USE_KIMI = True
    API_KEY = DEFAULT_KIMI_API_KEY
    BASE_URL = "https://api.moonshot.cn/v1"
else:
    raise ValueError("请设置 KIMI_API_KEY 或 OPENAI_API_KEY 环境变量")

# 模型配置
if USE_KIMI:
    LLM_MODEL = os.getenv("LLM_MODEL", "moonshot-v1-8k")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "")
else:
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# 百度 AI 搜索 API 配置
# 默认 API Key（如果不设置环境变量则使用此默认值）
DEFAULT_BAIDU_API_KEY = "bce-v3/ALTAK-ORrOi8rIakmsqdvPz7jqL/f182636d463e530fd831cd491ce4c19cbe9f6f40"

BAIDU_API_KEY = os.getenv("BAIDU_API_KEY") or DEFAULT_BAIDU_API_KEY

# RAG 配置
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "3"))

# Embedding 配置 - 如果使用 Kimi，需要使用本地 embedding
USE_LOCAL_EMBEDDING = USE_KIMI or not EMBEDDING_MODEL
