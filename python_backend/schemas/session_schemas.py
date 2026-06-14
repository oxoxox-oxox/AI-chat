from pydantic import BaseModel
from typing import Optional


class SessionCreate(BaseModel):
    title: Optional[str] = "新对话"
