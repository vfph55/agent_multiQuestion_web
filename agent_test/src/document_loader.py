"""文档加载和预处理模块."""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, KNOWLEDGE_BASE_DIR


def load_markdown_documents(directory: Path = KNOWLEDGE_BASE_DIR) -> List[Document]:
    """加载知识库中的所有 Markdown 文件.

    Args:
        directory: 知识库目录路径

    Returns:
        Document 对象列表
    """
    documents = []

    for file_path in directory.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        doc = Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
            }
        )
        documents.append(doc)

    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """将文档分割成小块.

    Args:
        documents: 原始文档列表

    Returns:
        分割后的文档块列表
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)
    return chunks
