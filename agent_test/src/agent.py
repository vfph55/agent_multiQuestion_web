"""主 Agent 模块 - 整合路由、RAG、搜索和通用 LLM."""

from typing import Literal, Optional

from src.rag_chain import ask_company_question
from src.llm_chain import ask_general_question
from src.search_chain import ask_realtime_question
from src.router import route_question, route_with_security_check
from src.session import SessionManager, Session
from src.formatter import format_answer


class KnowledgeAgent:
    """知识问答 Agent.

    功能：
    1. 自动判断问题类型（公司问题、实时问题、通用问题）
    2. 公司问题走 RAG 流程，检索知识库后回答
    3. 实时问题走搜索流程，联网获取最新信息后回答
    4. 通用问题直接调用 LLM 回答
    5. 支持多轮对话（通过 session 管理）
    """

    def __init__(self):
        """初始化 Agent."""
        self.session_manager = SessionManager()

    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, Session]:
        """获取或创建会话.

        Args:
            session_id: 会话ID，None则创建新会话

        Returns:
            (session_id, session对象)
        """
        return self.session_manager.get_or_create(session_id)

    def classify_question(self, question: str) -> Literal["company", "general", "realtime"]:
        """判断问题类型.

        Args:
            question: 用户问题

        Returns:
            "company"、"general" 或 "realtime"
        """
        return route_question(question)

    def answer(self, question: str, session_id: Optional[str] = None, format_type: str = "structured") -> dict:
        """回答用户问题（支持多轮对话）.

        Args:
            question: 用户问题
            session_id: 会话ID，None则创建新会话
            format_type: 格式化类型 - "structured"(结构化) | "plain"(纯文本) | "markdown"(原始)

        Returns:
            包含回答、路由信息和session_id的字典
        """
        # 1. 获取或创建会话
        sid, session = self.get_or_create_session(session_id)

        # 2. 安全检查 + 路由判断
        question_type, security_message = route_with_security_check(question)

        # 3. 如果被拦截，直接返回拒绝消息
        if question_type == "blocked":
            return {
                "question": question,
                "question_type": "blocked",
                "source": "security_filter",
                "answer": security_message,
                "structured": None,
                "session_id": sid,
            }

        # 4. 获取对话历史
        history = session.get_history()

        # 5. 根据类型选择处理方式，传入历史记录
        if question_type == "company":
            answer = ask_company_question(question, history)
            source = "rag"
        elif question_type == "realtime":
            answer = ask_realtime_question(question, history)
            source = "search"
        else:
            answer = ask_general_question(question, history)
            source = "llm"

        # 6. 格式化答案（转换为结构化数据）
        formatted_answer = format_answer(answer, format_type)

        # 7. 保存对话到历史（保存原始文本）
        session.add_message("user", question)
        session.add_message("assistant", answer)

        return {
            "question": question,
            "question_type": question_type,
            "source": source,
            "answer": answer,  # 原始 Markdown 文本
            "structured": formatted_answer if format_type == "structured" else None,
            "session_id": sid,
        }


def ask(question: str, session_id: Optional[str] = None) -> str:
    """快速问答函数.

    Args:
        question: 用户问题
        session_id: 会话ID，None则创建新会话

    Returns:
        回答内容
    """
    agent = KnowledgeAgent()
    result = agent.answer(question, session_id)
    return result["answer"]
