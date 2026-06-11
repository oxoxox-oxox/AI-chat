import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());

// 托管 test-stream.html：浏览器打开 http://localhost:3000 即可测试
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'test-stream.html'));
});

const OLLAMA_URL = 'http://localhost:11434/api/generate';
const MODEL = 'gemma:latest'; // 你本地已有的模型

app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;

    // 向 Ollama 发送请求
    const response = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        prompt: message,
        stream: false, // 第一阶段先关掉流式，拿完整回复
      }),
    });

    const data = await response.json();
    res.json({ reply: data.response });
  } catch (err) {
    console.error('请求 Ollama 失败:', err.message);
    res.status(500).json({ error: 'AI 服务暂时不可用，请确认 Ollama 已启动' });
  }
});

// ============================================================
// 第二阶段：流式传输 (SSE) —— 让 AI 回复逐字"蹦"出来
// ============================================================

app.post('/api/chat/stream', async (req, res) => {
  const { message } = req.body;

  // ① 设置 SSE 必需的三个响应头
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders(); // 立即把响应头发给客户端，不要等 body

  try {
    // ② 请求 Ollama，stream: true 开启流式模式
    const response = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        prompt: message,
        stream: true,
      }),
    });

    // ③ 拿到可读流，用 getReader() 逐块读取
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';   // 缓冲区：处理跨 chunk 的不完整行

    while (true) {
      const { done, value } = await reader.read();
      if (done) break; // 流结束

      // 把二进制数据解码成文本，拼到缓冲区
      buffer += decoder.decode(value, { stream: true });

      // 按换行符切分，最后一段（可能不完整）留在 buffer
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;

        try {
          const parsed = JSON.parse(line);
          // Ollama 返回的每一行：{ "response": "一个词", "done": false }
          res.write(`data: ${JSON.stringify({ content: parsed.response })}\n\n`);

          if (parsed.done) {
            res.write('data: [DONE]\n\n');
          }
        } catch {
          // JSON 解析失败就跳过（空白行、不完整行等）
        }
      }
    }
  } catch (err) {
    console.error('流式请求失败:', err.message);
    res.write(`data: ${JSON.stringify({ error: err.message })}\n\n`);
  } finally {
    res.end(); // 无论如何都要关闭连接
  }
});

// ============================================================

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`✅ 服务器已启动: http://localhost:${PORT}`);
  console.log(`📡 Ollama 模型: ${MODEL}`);
});
