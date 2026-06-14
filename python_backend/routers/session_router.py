"""
会话路由
"""
from fastapi import APIRouter

from schemas.session_schemas import SessionCreate
from services.session_service import create_session, list_sessions, delete_session

router = APIRouter(prefix="/api/sessions", tags=["会话"])


@router.post("/")
async def create(data: SessionCreate):
    """创建新会话"""
    session_id = create_session(data.title)
    return {"sessionId": session_id, "title": data.title}


@router.get("/")
async def list_all():
    """获取所有会话列表（按更新时间降序）"""
    return list_sessions()


@router.get("/{session_id}/messages")
async def get_messages(session_id: int, limit: int = 10):
    """获取指定对话的最近N条历史消息"""
    from services.chat_service import get_messages
    return get_messages(session_id, limit)


@router.delete("/{session_id}")
async def delete(session_id: int):
    """删除指定会话及其所有消息"""
    delete_session(session_id)
    return {"ok": True}
