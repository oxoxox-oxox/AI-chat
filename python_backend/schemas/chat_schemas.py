from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[int] = None
