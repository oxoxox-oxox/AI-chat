"""
集中配置模块 —— 所有环境变量在这里读取一次
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ---- 数据库 ----
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "ollama_chat")

# ---- 服务器 ----
PORT = int(os.getenv("PORT", 3000))

# ---- Ollama ----
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5")
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"

# ---- RAG ----
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
EMBED_URL = f"{OLLAMA_HOST}/api/embeddings"