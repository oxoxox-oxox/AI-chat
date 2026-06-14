"""
RAG 服务：文档切块、向量化、存储、检索
"""
import asyncio

import chromadb
import httpx

from config import EMBED_URL, EMBED_MODEL

# ---- 初始化 ChromaDB 客户端（数据持久化到 ./chroma_data） ----
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# ---- 获取或创建集合（类似 MySQL 的 table） ----
collection = chroma_client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"},  # 用余弦相似度
)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    切块函数：把长文本切成小块，块之间有重叠
    500 字一块，50 字重叠 —— 防止关键句被拦腰切断
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


async def get_embedding(text: str) -> list[float]:
    """
    调 Ollama Embedding API，把文字转成向量
    返回：[0.12, -0.34, 0.56, ...]  768 个浮点数
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            EMBED_URL,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=60.0,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]


async def index_document(file_name: str, content: str) -> int:
    """
    索引文档：
    1. 读内容 → 2. 切块 → 3. 每块向量化 → 4. 存 ChromaDB
    返回块数量
    """
    chunks = chunk_text(content)
    if not chunks:
        return 0

    # 并行向量化所有块
    embeddings = await asyncio.gather(
        *[get_embedding(c) for c in chunks]
    )

    # 生成唯一 ID（基于已有数量）
    base_id = collection.count()
    ids = [f"chunk_{base_id + i}" for i in range(len(chunks))]
    metadatas = [
        {"file_name": file_name, "chunk_idx": i}
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)


async def query_documents(query: str, n_results: int = 5) -> list[dict]:
    """
    检索相关文档块：
    1. 问题向量化 → 2. ChromaDB 余弦相似度搜索 → 3. 返回 Top-K
    """
    if collection.count() == 0:
        return []

    query_emb = await get_embedding(query)

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=min(n_results, collection.count()),
    )

    formatted = []
    if results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            formatted.append({
                "content": doc,
                "file_name": meta["file_name"],
                "chunk_idx": meta["chunk_idx"],
            })

    return formatted


def get_stats() -> dict:
    """返回索引统计"""
    return {
        "total_chunks": collection.count(),
    }
