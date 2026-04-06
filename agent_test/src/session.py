"""会话管理模块 - 存储多轮对话历史."""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Session:
    """会话数据类."""
    session_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    last_active: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str):
        """添加消息到历史记录."""
        self.messages.append({"role": role, "content": content})
        self.last_active = time.time()

    def get_history(self, max_turns: int = 10) -> str:
        """获取格式化的历史对话（最近 N 轮）."""
        # 每轮包含 user + assistant 两条消息
        max_messages = max_turns * 2
        recent_messages = self.messages[-max_messages:]

        history_parts = []
        for msg in recent_messages:
            role_label = "用户" if msg["role"] == "user" else "助手"
            history_parts.append(f"{role_label}: {msg['content']}")

        return "\n\n".join(history_parts)

    def is_expired(self, timeout_hours: int = 24) -> bool:
        """检查会话是否过期."""
        return time.time() - self.last_active > timeout_hours * 3600


class SessionManager:
    """会话管理器 - 内存存储（可用 Redis 替换）."""

    def __init__(self, max_sessions: int = 1000):
        """初始化.

        Args:
            max_sessions: 最大会话数，超过会清理最旧的
        """
        self._sessions: Dict[str, Session] = {}
        self._max_sessions = max_sessions

    def get_or_create(self, session_id: Optional[str]) -> tuple[str, Session]:
        """获取或创建会话.

        Args:
            session_id: 会话ID，None则创建新会话

        Returns:
            (session_id, session对象)
        """
        import uuid

        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            session.last_active = time.time()
            return session_id, session

        # 创建新会话
        new_id = session_id or str(uuid.uuid4())[:8]
        session = Session(session_id=new_id)
        self._sessions[new_id] = session

        # 清理过期会话
        self._cleanup_expired()

        return new_id, session

    def _cleanup_expired(self):
        """清理过期和超量的会话."""
        # 先删除过期会话
        expired = [
            sid for sid, s in self._sessions.items()
            if s.is_expired()
        ]
        for sid in expired:
            del self._sessions[sid]

        # 如果还超量，删除最旧的
        if len(self._sessions) > self._max_sessions:
            sorted_sessions = sorted(
                self._sessions.items(),
                key=lambda x: x[1].last_active
            )
            to_remove = len(self._sessions) - self._max_sessions
            for sid, _ in sorted_sessions[:to_remove]:
                del self._sessions[sid]


# 全局会话管理器实例
session_manager = SessionManager()
