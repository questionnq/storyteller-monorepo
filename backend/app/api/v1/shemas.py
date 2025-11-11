from pydantic import BaseModel, Field
from typing import Optional

class ScriptRequest(BaseModel):
    prompt: Optional[str] = Field(None, max_length=300, description="Идея для видео")
    genre: Optional[str] = Field(None, max_length=50)
    style: Optional[str] = Field(None, max_length=50)
    time: float = Field(30.0, ge=10, le=180, description="Общая длительность видео в секундах")
