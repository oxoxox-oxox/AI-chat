"""
聊天路由：非流式 & 流式对话
"""
import json

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from config import OLLAMA_CHAT_URL, OLLAMA_MODEL
from schemas.chat_schemas import ChatRequest
from services.chat_service import build_context, save_message, build_rag_messages
from services.session_service import create_session

router = APIRouter(prefix="/api/chat", tags=["聊天"])


def _ensure_session(session_id: int | None, message: str) -> int:
    """没有 sessionId 则自动创建，返回有效的 session_id"""
    if session_id:
        return session_id
    return create_session(message[:30] or "新对话")


@router.post("/")
async def chat(req: ChatRequest):
    """非流式对话接口"""
    sid = _ensure_session(req.sessionId, req.message)

    save_message(sid, "user", req.message)
    messages = build_context(sid, req.message)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_CHAT_URL,
                json={"model": OLLAMA_MODEL,
                      "messages": messages, "stream": False},
                timeout=120.0,
            )
        data = response.json()
        reply = data.get("message", {}).get("content", "")

        if reply:
            save_message(sid, "assistant", reply)

        return {"sessionId": sid, "reply": reply}
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Ollama 服务不可用: {str(e)}")


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """流式对话接口（SSE）"""
    sid = _ensure_session(req.sessionId, req.message)

    save_message(sid, "user", req.message)
    if req.rag:
        messages = await build_rag_messages(sid, req.message)
    else:
        messages = build_context(sid, req.message)

    async def event_generator():
        full_reply = ""
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    OLLAMA_CHAT_URL,
                    json={"model": OLLAMA_MODEL,
                          "messages": messages, "stream": True},
                    timeout=120.0,
                ) as response:
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            content = chunk.get(
                                "message", {}).get("content", "")
                            if content:
                                full_reply += content
                                yield f"data: {json.dumps({'content': content})}\n\n"
                            if chunk.get("done"):
                                yield "data: [DONE]\n\n"
                        except json.JSONDecodeError:
                            continue

            if full_reply:
                save_message(sid, "assistant", full_reply)

            yield f"data: {json.dumps({'sessionId': sid})}\n\n"

        except httpx.RequestError as e:
            yield f"data: {json.dumps({'error': f'Ollama 服务不可用: {str(e)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
