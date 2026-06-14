"""
聊天服务：上下文构建、消息存储
"""
from db import get_connection


def build_context(session_id: int, current_message: str, limit: int = 20) -> list[dict]:
    """从数据库捞出最近的 limit 条历史消息，返回 Ollama messages 数组"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at ASC LIMIT %s",
        (session_id, limit),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    messages = [{"role": r["role"], "content": r["content"]} for r in rows]
    messages.append({"role": "user", "content": current_message})
    return messages


def save_message(session_id: int, role: str, content: str):
    """保存消息并更新会话的 updated_at"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
        (session_id, role, content),
    )
    cursor.execute(
        "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
        (session_id,),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_messages(session_id: int, limit: int = 10) -> list[dict]:
    """获取指定会话的最近 limit 条消息"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at DESC LIMIT %s",
        (session_id, limit),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # 反转回时间升序
    rows.reverse()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


async def build_rag_messages(session_id: int, current_message: str, limit: int = 20) -> list[dict]:
    """
    构建带 RAG 文档上下文的 messages 数组
    流程：MySQL历史 + ChromaDB检索 -> 拼系统提示 -> 返回完整 messages
    """
    from services.rag_service import query_documents

    # 拿常规历史 + 当前问题的messages
    messages = build_context(session_id, current_message, limit)

    # 去ChromaDB 检索相关文档块
    docs = await query_documents(current_message, n_results=5)

    if docs:
        # 拼接
        doc_context = "\n\n---\n\n".join(
            f"[来源： {d['file_name']}]\n{d['content']}"
            for d in docs
        )
        # 在 messages 最前面插入系统提示
        system_msg = {
            "role": "system",
            "content": (
                "你是一个基于文档知识库的角色扮演者。"
                "请根据以下参考文档回答用户。"
                f"===参考文档===\n{doc_context}\n===文档结束==="
            ),
        }
        messages.insert(0, system_msg)
        
    return messages