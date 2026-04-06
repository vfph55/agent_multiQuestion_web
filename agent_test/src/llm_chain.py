"""通用 LLM 调用链模块."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from src.config import LLM_MODEL, USE_KIMI, BASE_URL, API_KEY

# 通用问题 Prompt 模板
GENERAL_PROMPT_TEMPLATE = """你是一个 helpful 的 AI 助手。请根据对话历史回答用户问题。

=== 对话历史 ===
{history}
================

当前问题：{question}

请用中文回答："""


def create_llm_chain():
    """创建通用 LLM 调用链.

    直接调用 LLM，不添加额外上下文。

    Returns:
        可运行的 LangChain 链
    """
    # 创建 LLM
    if USE_KIMI:
        llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0.7,
            openai_api_base=BASE_URL,
            openai_api_key=API_KEY,
        )
    else:
        llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0.7,
        )

    # 创建 Prompt
    prompt = PromptTemplate.from_template(GENERAL_PROMPT_TEMPLATE)

    # 构建链
    chain = (
        {"question": lambda x: x["question"], "history": lambda x: x.get("history", "")}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def ask_general_question(question: str, history: str = "") -> str:
    """回答通用问题.

    Args:
        question: 用户问题
        history: 对话历史

    Returns:
        回答内容
    """
    chain = create_llm_chain()
    return chain.invoke({"question": question, "history": history})
