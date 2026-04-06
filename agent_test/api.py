#!/usr/bin/env python3
"""FastAPI 服务 - 知识问答 Agent API."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal, List
from pathlib import Path

from src.agent import KnowledgeAgent

# 创建 FastAPI 应用
app = FastAPI(
    title="ZURU Melon 知识问答 API",
    description="智能知识问答系统 - 自动区分公司问题和通用问题",
    version="1.0.0"
)

# 全局 Agent 实例
agent = None

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "static"


@app.on_event("startup")
async def startup_event():
    """启动时初始化 Agent."""
    global agent
    print("🚀 正在初始化 Agent...")
    agent = KnowledgeAgent()
    print("✅ Agent 初始化完成")


# 请求模型
class QuestionRequest(BaseModel):
    question: str
    session_id: str | None = None


# 结构化段落
class Section(BaseModel):
    type: str  # heading, paragraph, list, code
    content: str = ""
    level: int = 0  # for heading
    list_type: str = ""  # for list: ul or ol
    items: list = []  # for list


# 结构化答案
class StructuredAnswer(BaseModel):
    title: str
    sections: list[Section]


# 响应模型
class AnswerResponse(BaseModel):
    question: str
    answer: str
    session_id: str
    source: str
    question_type: str
    structured: StructuredAnswer | None = None


# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
async def serve_index():
    """返回首页 HTML."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api")
async def root():
    """API 状态."""
    return {
        "service": "ZURU Melon 知识问答 API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查."""
    return {"status": "healthy", "agent_ready": agent is not None}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """回答问题（支持多轮对话）.

    - **question**: 用户问题
    - **session_id**: 会话ID（可选，不传则创建新会话）

    Agent 自动判断问题类型并选择合适的回答方式，支持多轮对话上下文
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent 未初始化")

    try:
        result = agent.answer(request.question, request.session_id, format_type="structured")

        # 构建结构化响应
        structured_data = result.get("structured")
        sections = []
        if structured_data and "sections" in structured_data:
            for sec in structured_data["sections"]:
                sections.append(Section(
                    type=sec.get("type", "paragraph"),
                    content=sec.get("content", ""),
                    level=sec.get("level", 0),
                    list_type=sec.get("list_type", ""),
                    items=sec.get("items", [])
                ))

        structured_answer = StructuredAnswer(
            title=structured_data.get("title", "") if structured_data else "",
            sections=sections
        ) if structured_data else None

        # 返回答案、session_id 和来源信息，用于后续对话
        return AnswerResponse(
            question=result["question"],
            answer=result["answer"] if isinstance(result["answer"], str) else str(result["answer"]),
            session_id=result["session_id"],
            source=result["source"],
            question_type=result["question_type"],
            structured=structured_answer
        )
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
