"""实时搜索问答链模块 - 使用百度 AI 搜索 API."""

import json
import os
from datetime import datetime, timedelta

import requests
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from src.config import LLM_MODEL, USE_KIMI, BASE_URL, API_KEY, BAIDU_API_KEY

# 实时问答 Prompt 模板
REALTIME_PROMPT_TEMPLATE = """你是一个智能助手。基于以下实时搜索结果和对话历史，回答用户的问题。

=== 实时搜索结果 ===
{search_results}
==================

=== 对话历史 ===
{history}
================

请根据以上信息回答当前问题。

重要：如果搜索结果显示"未找到"或"搜索出错"，请明确告知用户无法获取实时信息，不要编造答案。

当前问题：{question}

请用中文回答："""


def baidu_ai_search(query: str, count: int = 10, freshness: str = None) -> list:
    """使用百度 AI 搜索 API 搜索网络.

    Args:
        query: 搜索关键词
        count: 返回结果数量 (1-50)
        freshness: 时间范围 (pd=过去24小时, pw=过去7天, pm=过去31天, py=过去365天, 或 YYYY-MM-DDtoYYYY-MM-DD)

    Returns:
        搜索结果列表
    """
    if not BAIDU_API_KEY:
        raise ValueError("请设置 BAIDU_API_KEY 环境变量")

    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"

    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }

    # 构建时间过滤
    search_filter = {}
    if freshness:
        current_time = datetime.now()
        end_date = (current_time + timedelta(days=1)).strftime("%Y-%m-%d")

        if freshness == "pd":
            start_date = (current_time - timedelta(days=1)).strftime("%Y-%m-%d")
            search_filter = {"range": {"page_time": {"gte": start_date, "lt": end_date}}}
        elif freshness == "pw":
            start_date = (current_time - timedelta(days=6)).strftime("%Y-%m-%d")
            search_filter = {"range": {"page_time": {"gte": start_date, "lt": end_date}}}
        elif freshness == "pm":
            start_date = (current_time - timedelta(days=30)).strftime("%Y-%m-%d")
            search_filter = {"range": {"page_time": {"gte": start_date, "lt": end_date}}}
        elif freshness == "py":
            start_date = (current_time - timedelta(days=364)).strftime("%Y-%m-%d")
            search_filter = {"range": {"page_time": {"gte": start_date, "lt": end_date}}}
        elif "to" in freshness:
            # YYYY-MM-DDtoYYYY-MM-DD 格式
            dates = freshness.split("to")
            if len(dates) == 2:
                search_filter = {"range": {"page_time": {"gte": dates[0], "lt": dates[1]}}}

    request_body = {
        "messages": [
            {
                "content": query,
                "role": "user"
            }
        ],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": min(max(count, 1), 50)}],
        "search_filter": search_filter
    }

    try:
        response = requests.post(url, json=request_body, headers=headers, timeout=30)
        response.raise_for_status()
        results = response.json()

        if "code" in results:
            raise Exception(results.get("message", "搜索失败"))

        return results.get("references", [])
    except Exception as e:
        raise Exception(f"搜索请求失败: {str(e)}")


def search_web(query: str, max_results: int = 5, freshness: str = "pd") -> str:
    """搜索网络并格式化结果.

    Args:
        query: 搜索关键词
        max_results: 最大结果数
        freshness: 时间范围 (pd=过去24小时)

    Returns:
        格式化的搜索结果字符串
    """
    try:
        results = baidu_ai_search(query, count=max_results, freshness=freshness)

        if not results:
            return "未找到相关搜索结果。"

        formatted = []
        for i, item in enumerate(results[:max_results], 1):
            title = item.get("title", "无标题")
            content = item.get("content", item.get("summary", "无内容"))
            url = item.get("url", "")

            formatted.append(f"[{i}] {title}\n{content}\n来源: {url}\n")

        return "\n".join(formatted)

    except Exception as e:
        return f"搜索出错: {str(e)}"


def create_search_chain():
    """创建实时搜索问答链.

    流程：搜索 -> 构建 Prompt -> LLM 生成答案

    Returns:
        可运行的函数
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
    prompt = PromptTemplate.from_template(REALTIME_PROMPT_TEMPLATE)

    # 构建链
    chain = (
        {
            "search_results": lambda x: x["search_results"],
            "question": lambda x: x["question"],
            "history": lambda x: x.get("history", "")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def ask_realtime_question(question: str, history: str = "") -> str:
    """回答实时性问题.

    Args:
        question: 用户问题
        history: 对话历史

    Returns:
        回答内容
    """
    # 1. 检查 API Key
    if not BAIDU_API_KEY:
        return "❌ 无法获取实时信息：请设置 BAIDU_API_KEY 环境变量。\n\n获取方式：https://console.bce.baidu.com/ai-search/qianfan/ais/console/apiKey"

    try:
        # 2. 搜索网络
        search_results = search_web(question, max_results=5, freshness="pd")

        # 3. 检查搜索结果是否有效
        if "搜索出错" in search_results:
            return f"❌ 无法获取实时信息：搜索服务暂时不可用。\n\n错误详情：{search_results}"

        if search_results == "未找到相关搜索结果。":
            return "❌ 无法获取实时信息：未找到相关搜索结果。请尝试更换关键词。"

        # 4. 创建链并生成答案
        chain = create_search_chain()
        answer = chain.invoke({
            "search_results": search_results,
            "question": question,
            "history": history
        })

        # 5. 在答案前标注来源
        return f"🔍 基于实时搜索结果：\n\n{answer}"

    except Exception as e:
        return f"❌ 处理失败：{str(e)}"
