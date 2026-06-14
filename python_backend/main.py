"""
AI Chat — FastAPI 入口（单用户版）
启动: python main.py
API 文档: http://localhost:3000/docs
"""
import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import PORT, OLLAMA_MODEL
from db import init_db
from routers import session_router, chat_router, rag_router

app = FastAPI(title="Ollama AI Chat")

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 注册路由 ----
app.include_router(session_router)
app.include_router(chat_router)
app.include_router(rag_router)


# ---- 根路由 ----
@app.get("/", response_class=HTMLResponse)
async def root():
    """返回测试页面"""
    html_path = pathlib.Path(__file__).parent.parent / "test-stream.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")

    return """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>Ollama Chat Test</title>
    <style>
        body { font-family: system-ui; max-width: 700px; margin: 50px auto; padding: 0 20px; }
        .bar { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
        input { flex: 1; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; border-radius: 6px; border: none; background: #4f46e5; color: #fff; }
        button.new { background: #e5e7eb; color: #333; }
        #status { font-size: 13px; color: #888; }
        #output { margin-top: 20px; padding: 16px; background: #f5f5f5; border-radius: 8px; min-height: 100px; white-space: pre-wrap; }
        .cursor::after { content: '▊'; animation: blink 1s steps(1) infinite; }
        @keyframes blink { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <h2>🤖 Ollama Chat (FastAPI)</h2>
    <div class="bar">
        <input id="input" type="text" placeholder="输入你的问题..." value="我叫小明">
        <button onclick="send()">发送</button>
        <button class="new" onclick="newChat()">新对话</button>
    </div>
    <div id="status"></div>
    <div id="output"></div>
    <script>
        let sessionId = null;
        function setStatus(t) { document.getElementById('status').textContent = t; }
        function newChat() { sessionId = null; document.getElementById('output').innerHTML = ''; setStatus('新对话'); }
        async function send() {
            const msg = document.getElementById('input').value;
            if (!msg.trim()) return;
            const output = document.getElementById('output');
            output.innerHTML = '';
            output.classList.add('cursor');
            setStatus('思考中...');
            const body = { message: msg };
            if (sessionId) body.sessionId = sessionId;
            const res = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\\n');
                buffer = lines.pop();
                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) output.innerHTML += parsed.content;
                        if (parsed.sessionId) { sessionId = parsed.sessionId; setStatus('对话 ID: ' + sessionId); }
                    } catch(e) {}
                }
            }
            output.classList.remove('cursor');
        }
        document.addEventListener('keypress', e => { if(e.key === 'Enter') send(); });
    </script>
</body>
</html>"""


# ---- 启动入口 ----
if __name__ == "__main__":
    import uvicorn

    init_db()
    print(f"Ollama 模型: {OLLAMA_MODEL}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
