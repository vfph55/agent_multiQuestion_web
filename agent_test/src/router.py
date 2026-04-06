"""路由判断模块：区分公司问题和通用问题."""

from typing import Literal

from src.config import LLM_MODEL, USE_KIMI, BASE_URL, API_KEY


# 尝试导入 Sentence-BERT，如果没安装则回退到 LLM
try:
    from src.security_filter import check_security, classify_intent_sbert
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠️  sentence-transformers 未安装，将使用 LLM 路由")


def create_router_llm():
    """创建用于路由判断的轻量级 LLM."""
    from langchain_openai import ChatOpenAI

    if USE_KIMI:
        return ChatOpenAI(
            model="moonshot-v1-8k",
            temperature=0.0,
            openai_api_base=BASE_URL,
            openai_api_key=API_KEY,
        )
    else:
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.0,
        )


def route_with_llm(question: str) -> Literal["company", "general", "realtime"]:
    """使用 LLM 判断问题类型."""
    from langchain_core.messages import HumanMessage

    llm = create_router_llm()

    prompt = f"""分析以下问题，判断它属于哪种类型：

1. "company" - 公司问题：询问公司政策、规定、流程、工作环境、编码规范等
2. "realtime" - 实时问题：询问需要时间敏感信息的问题（如新闻、股价、时事等）
3. "general" - 通用问题：编程技术、AI概念、生活常识等静态知识

只回答一个字："company"、"realtime" 或 "general"

问题：{question}

类型："""

    response = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()

    if "company" in response:
        return "company"
    elif "realtime" in response:
        return "realtime"
    else:
        return "general"


def route_question(question: str) -> Literal["company", "general", "realtime"]:
    """判断问题类型.

    三级架构：
    1. 关键词快速匹配（实时问题）
    2. Sentence-BERT 语义识别（公司/通用）
    3. LLM 兜底判断（模糊/新问题）

    Args:
        question: 用户问题

    Returns:
        "company" 表示公司相关问题，走 RAG 流程
        "general" 表示通用问题，直接调用 LLM
        "realtime" 表示实时性问题，需要网络搜索
    """
    # 1. 关键词快速判断（零成本）
    question_lower = question.lower()
    realtime_keywords = [
        '今天', '现在', '当前', '最新', '新闻', '天气', '股价', '股票',
        '汇率', '比分', '比赛结果', '今日', '本周', '本月', '今年',
        '实时', '今天日期', '现在时间', '金价', '油价', '彩票',
        '涨停', '大跌', '大涨', '热搜', '热门'
    ]

    for keyword in realtime_keywords:
        if keyword in question_lower:
            return "realtime"

    # 2. 如果 Sentence-BERT 可用，进行语义识别
    if SBERT_AVAILABLE:
        intent, score = classify_intent_sbert(question)

        if intent != "uncertain":
            # Sentence-BERT 识别成功
            return intent

        # 相似度太低，降级到 LLM
        return route_with_llm(question)

    # 3. 回退到纯 LLM 判断
    return route_with_llm(question)


def route_with_security_check(question: str) -> tuple[Literal["company", "general", "realtime", "blocked"], str]:
    """带安全检查的路由.

    Returns:
        (路由结果, 说明信息)
        如果 blocked，说明信息是拒绝原因
    """
    # 1. 安全检查（如果可用）
    if SBERT_AVAILABLE:
        from src.security_filter import check_security
        status, message = check_security(question)
        if status == "blocked":
            return "blocked", message

    # 2. 正常路由
    result = route_question(question)
    return result, ""
