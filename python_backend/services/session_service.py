"""
会话管理服务：创建、查询会话
"""
from db import get_connection


def create_session(title: str) -> int:
    """创建新会话，返回 session_id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (title) VALUES (%s)",
        (title or "新对话",),
    )
    session_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return session_id


def list_sessions() -> list[dict]:
    """列出所有会话（按更新时间降序）"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, title, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def delete_session(session_id: int):
    """删除指定会话（CASCADE 自动删除关联消息）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
    conn.commit()
    cursor.close()
    conn.close()
