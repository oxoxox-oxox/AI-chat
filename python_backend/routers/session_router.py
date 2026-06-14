"""
会话路由
"""
from fastapi import APIRouter

from schemas.session_schemas import SessionCreate
from services.session_service import create_session, list_sessions

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
