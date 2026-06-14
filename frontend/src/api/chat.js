/**
 * 后端 API 封装
 */
const BASE = '/api'

export async function createSession(title = '新对话') {
  const res = await fetch(`${BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
  if (!res.ok) throw new Error('创建会话失败')
  return res.json()
}

export async function fetchSessions() {
  const res = await fetch(`${BASE}/sessions`)
  if (!res.ok) throw new Error('获取会话列表失败')
  return res.json()
}

/**
 * SSE 流式对话
 * @param {string} message
 * @param {number|null} sessionId
 * @param {(chunk: string) => void} onChunk  每收到一段文本
 * @param {(sessionId: number) => void} onDone  流结束
 * @param {(error: string) => void} onError
 */
export async function streamChat(message, sessionId, onChunk, onDone, onError, rag = false) {
  const body = { message, rag }
  if (sessionId) body.sessionId = sessionId

  const res = await fetch(`${BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    onError(`请求失败: ${res.status}`)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const data = line.slice(6)
      if (data === '[DONE]') continue

      try {
        const parsed = JSON.parse(data)
        if (parsed.content) onChunk(parsed.content)
        if (parsed.sessionId) onDone(parsed.sessionId)
        if (parsed.error) onError(parsed.error)
      } catch {
        // 忽略解析失败的行
      }
    }
  }
}

export async function fetchMessages(sessionId) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/messages`)
  if (!res.ok) throw new Error('获取消息失败')
    return res.json()
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error('删除会话失败')
  return res.json()
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${BASE}/rag/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('上传文档失败')
  return res.json()
}

export async function fetchRagStats() {
  const res = await fetch(`${BASE}/rag/stats`)
  if (!res.ok) throw new Error('获取知识库状态失败')
  return res.json()
}