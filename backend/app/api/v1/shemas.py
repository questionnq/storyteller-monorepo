from pydantic import BaseModel, Field

class ScriptRequest(BaseModel):
    prompt: str | None = Field(max_length = 300)
    genre: str | None = Field(max_length = 50)
    style: str | None = Field(max_length = 50)
    time: float | None = Field(ge = 0, le = 150)
