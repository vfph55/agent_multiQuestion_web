"""向量嵌入和 FAISS 索引管理模块."""

from pathlib import Path
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config import (
    EMBEDDING_MODEL,
    USE_KIMI,
    API_KEY,
    BASE_URL,
    VECTOR_STORE_DIR,
)


def get_embeddings():
    """获取嵌入模型实例."""
    if USE_KIMI:
        # 使用本地轻量级嵌入模型 (使用 gte-small，无需 PyTorch)
        from langchain_community.embeddings import GPT4AllEmbeddings
        return GPT4AllEmbeddings(model_name="all-MiniLM-L6-v2.gguf2.f16.gguf")
    else:
        # 使用 OpenAI 嵌入模型
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def create_vector_store(documents: List[Document], index_name: str = "knowledge_base") -> FAISS:
    """从文档创建 FAISS 向量存储.

    Args:
        documents: 文档块列表
        index_name: 索引名称

    Returns:
        FAISS 向量存储实例
    """
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(documents, embeddings)

    # 保存索引
    save_path = VECTOR_STORE_DIR / index_name
    vector_store.save_local(str(save_path))

    return vector_store


def load_vector_store(index_name: str = "knowledge_base") -> FAISS | None:
    """加载已有的 FAISS 向量存储.

    Args:
        index_name: 索引名称

    Returns:
        FAISS 向量存储实例，如果不存在则返回 None
    """
    save_path = VECTOR_STORE_DIR / index_name

    if not save_path.exists():
        return None

    embeddings = get_embeddings()
    return FAISS.load_local(
        str(save_path),
        embeddings,
        allow_dangerous_deserialization=True
    )


def get_or_create_vector_store(
    documents: List[Document] | None = None,
    index_name: str = "knowledge_base"
) -> FAISS:
    """获取或创建向量存储.

    如果已有索引则加载，否则创建新的.

    Args:
        documents: 用于创建索引的文档（仅在索引不存在时使用）
        index_name: 索引名称

    Returns:
        FAISS 向量存储实例
    """
    # 尝试加载已有索引
    existing_store = load_vector_store(index_name)
    if existing_store is not None:
        return existing_store

    # 需要创建新索引但没有提供文档
    if documents is None:
        raise ValueError("向量索引不存在，需要提供文档来创建")

    # 创建新索引
    return create_vector_store(documents, index_name)
