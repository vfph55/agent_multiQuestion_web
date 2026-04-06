"""答案格式化模块 - 将 Markdown 转换为结构化数据."""

import re
from typing import Dict, List, Union


def parse_markdown_to_structured(text: str) -> Dict[str, Union[str, List]]:
    """将 Markdown 文本解析为结构化数据.

    返回结构化的段落列表，便于前端渲染成卡片。

    Args:
        text: Markdown 格式的文本

    Returns:
        {
            "title": str,
            "sections": [
                {
                    "type": "heading" | "paragraph" | "list" | "code",
                    "content": str,
                    "items": List[str] (仅 list 类型)
                }
            ]
        }
    """
    lines = text.strip().split('\n')
    sections = []
    current_list = []
    current_list_type = None  # 'ul' or 'ol'

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 跳过空行
        if not stripped:
            i += 1
            continue

        # 处理代码块
        if stripped.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if current_list:
                _flush_list(sections, current_list, current_list_type)
                current_list = []
                current_list_type = None
            sections.append({
                "type": "code",
                "content": '\n'.join(code_lines)
            })
            i += 1
            continue

        # 处理标题 (### 或 ## 或 #)
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', stripped)
        if heading_match:
            if current_list:
                _flush_list(sections, current_list, current_list_type)
                current_list = []
                current_list_type = None
            sections.append({
                "type": "heading",
                "content": heading_match.group(2).strip(),
                "level": len(heading_match.group(1))
            })
            i += 1
            continue

        # 处理无序列表
        ul_match = re.match(r'^[-*]\s+(.+)$', line)
        if ul_match:
            if current_list_type == 'ol':
                _flush_list(sections, current_list, current_list_type)
                current_list = []
            current_list_type = 'ul'
            current_list.append(_inline_format(ul_match.group(1)))
            i += 1
            continue

        # 处理有序列表
        ol_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if ol_match:
            if current_list_type == 'ul':
                _flush_list(sections, current_list, current_list_type)
                current_list = []
            current_list_type = 'ol'
            current_list.append(_inline_format(ol_match.group(2)))
            i += 1
            continue

        # 普通段落
        if current_list:
            _flush_list(sections, current_list, current_list_type)
            current_list = []
            current_list_type = None

        # 合并连续的非列表行作为段落
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_stripped = lines[i].strip()
            if not next_stripped or next_stripped.startswith(('#', '-', '*', '```')) or re.match(r'^\d+\.', next_stripped):
                break
            para_lines.append(next_stripped)
            i += 1

        sections.append({
            "type": "paragraph",
            "content": _inline_format(' '.join(para_lines))
        })
        continue

    # 刷新最后的列表
    if current_list:
        _flush_list(sections, current_list, current_list_type)

    return {
        "title": "",
        "sections": sections
    }


def _flush_list(sections: List[Dict], items: List[str], list_type: str):
    """将累积的列表项添加到 sections."""
    if items:
        sections.append({
            "type": "list",
            "list_type": list_type,  # 'ul' or 'ol'
            "items": items
        })


def _inline_format(text: str) -> str:
    """处理行内格式（粗体、代码、链接）."""
    # 粗体 **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # 行内代码 `code`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # 链接 [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text


def format_to_plain_text(text: str) -> str:
    """将 Markdown 转换为纯文本（用于非 Web 场景）."""
    # 移除代码块标记，保留内容
    text = re.sub(r'```\w*\n', '', text)
    text = re.sub(r'```', '', text)
    # 移除标题标记
    text = re.sub(r'^#{1,4}\s+', '', text, flags=re.MULTILINE)
    # 移除列表标记
    text = re.sub(r'^[-*]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', lambda m: f"{m.group(0).strip()}. ", text, flags=re.MULTILINE)
    # 移除粗体标记
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    # 移除行内代码标记
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 移除链接，保留文本
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text.strip()


def format_answer(text: str, format_type: str = "structured") -> Union[Dict, str]:
    """统一答案格式化入口.

    Args:
        text: 原始 Markdown 答案
        format_type: "structured" | "plain" | "markdown"

    Returns:
        格式化后的结果
    """
    if format_type == "structured":
        return parse_markdown_to_structured(text)
    elif format_type == "plain":
        return format_to_plain_text(text)
    else:
        return text
