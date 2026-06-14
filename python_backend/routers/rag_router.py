"""
RAG 路由：文档上传、知识库问答
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from services import rag_service

router = APIRouter(prefix="/api/rag", tags=["RAG 知识库"])


class RAGQuery(BaseModel):
    question: str


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档到知识库"""
    if not file.filename:
        raise HTTPException(400, "文件名不能为空")

    try:
        content = await file.read()
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("gbk")
        except Exception:
            raise HTTPException(400, "无法解码文件，请使用 UTF-8 编码的文本文件")

    if not text.strip():
        raise HTTPException(400, "文件内容为空")

    chunk_count = await rag_service.index_document(file.filename, text)

    return {
        "ok": True,
        "file_name": file.filename,
        "chunks": chunk_count,
    }


@router.post("/query")
async def rag_query(body: RAGQuery):
    """基于知识库的问答"""
    docs = await rag_service.query_documents(body.question, n_results=5)

    return {
        "question": body.question,
        "sources": docs,
    }


@router.get("/stats")
async def get_stats():
    """知识库统计"""
    return rag_service.get_stats()
