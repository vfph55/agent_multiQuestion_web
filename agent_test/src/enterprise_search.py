"""企业官网搜索模块 - 抓取公司官网信息."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re


class EnterpriseWebsiteSearcher:
    """企业官网搜索器."""

    def __init__(self, base_url: str = ""):
        """初始化.

        Args:
            base_url: 企业官网基础 URL，如 "https://www.zurumelon.com"
        """
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search(self, query: str, max_pages: int = 3) -> str:
        """搜索企业官网.

        策略：
        1. 先尝试抓取首页和常见页面
        2. 根据查询关键词匹配相关内容

        Args:
            query: 查询关键词
            max_pages: 最大抓取页面数

        Returns:
            格式化后的相关内容
        """
        if not self.base_url:
            return "未配置企业官网 URL"

        try:
            # 抓取关键页面
            pages_to_crawl = [
                "/",  # 首页
                "/about",  # 关于我们
                "/contact",  # 联系我们
                "/help",  # 帮助中心
                "/faq",  # 常见问题
                "/docs",  # 文档
                "/guide",  # 指南
            ]

            all_content = []
            crawled = 0

            for path in pages_to_crawl:
                if crawled >= max_pages:
                    break

                url = urljoin(self.base_url, path)
                content = self._fetch_page(url)

                if content:
                    all_content.append({
                        "url": url,
                        "title": content.get("title", ""),
                        "text": content.get("text", "")
                    })
                    crawled += 1

            # 根据查询词匹配最相关的内容
            return self._format_relevant_content(query, all_content)

        except Exception as e:
            return f"企业官网搜索失败: {str(e)}"

    def _fetch_page(self, url: str) -> Optional[Dict]:
        """抓取单个页面.

        Args:
            url: 页面 URL

        Returns:
            页面内容字典
        """
        if url in self.visited_urls:
            return None

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            self.visited_urls.add(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()

            # 提取标题
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""

            # 提取正文（优先选择主要内容区域）
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', class_=re.compile('content|main')) or
                soup.find('body')
            )

            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                # 清理多余空行
                text = re.sub(r'\n{3,}', '\n\n', text)
                # 限制长度
                text = text[:5000]
            else:
                text = ""

            return {"title": title_text, "text": text}

        except Exception as e:
            print(f"抓取页面失败 {url}: {e}")
            return None

    def _format_relevant_content(self, query: str, contents: List[Dict]) -> str:
        """格式化相关内容.

        简单的关键词匹配，提取最相关的段落.

        Args:
            query: 查询词
            contents: 页面内容列表

        Returns:
            格式化后的相关内容
        """
        if not contents:
            return "未找到相关内容"

        # 提取查询关键词
        query_keywords = set(query.lower().split())

        formatted = []
        for i, content in enumerate(contents, 1):
            title = content.get("title", "")
            text = content.get("text", "")
            url = content.get("url", "")

            # 简单的相关性评分
            text_lower = text.lower()
            match_score = sum(1 for kw in query_keywords if kw in text_lower)

            if match_score > 0 or i == 1:  # 至少包含第一个页面
                # 提取包含关键词的段落
                paragraphs = text.split('\n')
                relevant_paras = []

                for para in paragraphs[:20]:  # 限制段落数
                    para_lower = para.lower()
                    if any(kw in para_lower for kw in query_keywords) or len(para) > 50:
                        relevant_paras.append(para)

                if relevant_paras:
                    formatted.append(
                        f"[{i}] 来源：{title}\n"
                        f"URL: {url}\n"
                        f"{' '.join(relevant_paras[:5])}"  # 最多5个段落
                    )

        return "\n\n".join(formatted) if formatted else "未找到相关内容"


def search_enterprise_website(query: str, base_url: str = "") -> str:
    """搜索企业官网的便捷函数.

    Args:
        query: 查询关键词
        base_url: 企业官网 URL

    Returns:
        相关内容
    """
    # 从环境变量或配置中读取企业官网 URL
    if not base_url:
        import os
        base_url = os.getenv("ENTERPRISE_WEBSITE_URL", "")

    if not base_url:
        return "未配置企业官网 URL，请设置 ENTERPRISE_WEBSITE_URL 环境变量"

    searcher = EnterpriseWebsiteSearcher(base_url)
    return searcher.search(query)


if __name__ == "__main__":
    # 测试
    result = search_enterprise_website(
        "公司介绍",
        base_url="https://www.example.com"
    )
    print(result)
