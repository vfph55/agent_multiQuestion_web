"""RAG 检索链模块 - 三级检索策略：本地 RAG → 企业官网 → 通用 LLM."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from src.config import LLM_MODEL, USE_KIMI, BASE_URL, API_KEY, RETRIEVAL_TOP_K
from src.document_loader import load_markdown_documents, split_documents
from src.embeddings import get_or_create_vector_store
from src.enterprise_search import search_enterprise_website

# Prompt 模板
RAG_PROMPT_TEMPLATE = """你是一个专业的公司知识库助手。基于以下检索到的内容回答用户问题。

=== 检索到的相关内容 ===
{context}
==================

=== 对话历史 ===
{history}
================

请根据以上信息回答当前问题。请用中文回答，使用清晰的段落和列表格式。

如果以上信息不足以回答问题，请明确告知用户。

当前问题：{question}

回答："""

GENERAL_PROMPT_TEMPLATE = """你是一个 helpful 的 AI 助手。请回答用户问题。

=== 对话历史 ===
{history}
================

当前问题：{question}

请用中文回答："""

# 全局向量存储实例（延迟加载）
_vector_store = None


def get_vector_store():
    """获取向量存储实例（懒加载）."""
    global _vector_store
    if _vector_store is None:
        try:
            _vector_store = get_or_create_vector_store()
        except ValueError:
            print("📚 正在创建向量索引...")
            documents = load_markdown_documents()
            chunks = split_documents(documents)
            _vector_store = get_or_create_vector_store(documents=chunks)
            print(f"✅ 向量索引创建完成，共 {len(chunks)} 个文档块")
    return _vector_store


def retrieve_local_documents(question: str, k: int = None):
    """检索本地知识库.

    Returns:
        (文档内容, 文档列表)
    """
    if k is None:
        k = RETRIEVAL_TOP_K

    vector_store = get_vector_store()
    docs = vector_store.similarity_search(question, k=k)

    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("filename", "未知")
        content = doc.page_content.strip()
        formatted.append(f"[{i}] 来源：{source}\n{content}")

    return "\n\n".join(formatted), docs


def is_relevant(docs, question: str, threshold: float = 0.5) -> bool:
    """判断检索结果是否足够相关.

    策略：
    1. 只要有检索到文档就认为是相关的（FAISS已经做了相似度筛选）
    2. 或者检查文档内容是否包含问题关键词

    Args:
        docs: 检索到的文档列表
        question: 用户问题
        threshold: 相关性阈值

    Returns:
        是否相关
    """
    if not docs:
        return False

    # FAISS 已经返回了最相似的文档，只要有文档就认为相关
    # 但为了更严格，检查是否有实质内容
    for doc in docs:
        if len(doc.page_content.strip()) > 50:  # 文档内容足够长
            return True

    return False


def create_llm(temperature: float = 0.7):
    """创建 LLM 实例."""
    if USE_KIMI:
        return ChatOpenAI(
            model=LLM_MODEL,
            temperature=temperature,
            openai_api_base=BASE_URL,
            openai_api_key=API_KEY,
        )
    else:
        return ChatOpenAI(
            model=LLM_MODEL,
            temperature=temperature,
        )


def ask_with_fallback(question: str, history: str = "") -> str:
    """三级检索回答.

    策略：
    1. 先检索本地知识库
    2. 如果不相关，搜索企业官网
    3. 如果还没有，使用通用 LLM

    Returns:
        回答内容（包含来源标记）
    """
    llm = create_llm()

    # ========== Level 1: 本地 RAG ==========
    print(f"🔍 Level 1: 检索本地知识库...")
    local_context, docs = retrieve_local_documents(question)

    if docs and is_relevant(docs, question):
        print(f"✅ 本地知识库找到相关内容")
        prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        chain = (
            {
                "context": lambda x: local_context,
                "question": lambda x: x["question"],
                "history": lambda x: x.get("history", "")
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        answer = chain.invoke({"question": question, "history": history})
        return f"📚 [本地知识库]\n\n{answer}"

    print(f"⚠️ 本地知识库内容不足，降级到企业官网...")

    # ========== Level 2: 企业官网 ==========
    print(f"🔍 Level 2: 搜索企业官网...")
    web_context = search_enterprise_website(question)

    # 检查官网搜索是否有实质内容
    has_web_content = (
        web_context and
        "未找到" not in web_context and
        "未配置" not in web_context and
        "失败" not in web_context and
        len(web_context) > 50
    )

    if has_web_content:
        print(f"✅ 企业官网找到相关内容")
        prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        chain = (
            {
                "context": lambda x: web_context,
                "question": lambda x: x["question"],
                "history": lambda x: x.get("history", "")
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        answer = chain.invoke({"question": question, "history": history})
        return f"🌐 [企业官网]\n\n{answer}"

    print(f"⚠️ 企业官网无相关内容或未配置，使用通用 LLM...")

    # ========== Level 3: 通用 LLM ==========
    print(f"🤖 Level 3: 调用通用 LLM...")
    prompt = PromptTemplate.from_template(GENERAL_PROMPT_TEMPLATE)
    chain = (
        {
            "question": lambda x: x["question"],
            "history": lambda x: x.get("history", "")
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    answer = chain.invoke({"question": question, "history": history})
    return f"🤖 [通用知识]\n\n{answer}"


def ask_company_question(question: str, history: str = "") -> str:
    """回答公司相关问题（使用三级检索）.

    Args:
        question: 用户问题
        history: 对话历史

    Returns:
        回答内容
    """
    # 确保向量存储已初始化
    get_vector_store()

    return ask_with_fallback(question, history)
