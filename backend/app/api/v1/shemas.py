from pydantic import BaseModel, Field
from typing import Optional, List


class ScriptRequest(BaseModel):
    prompt: Optional[str] = Field(None, max_length=300, description="Идея для видео")
    genre: Optional[str] = Field(None, max_length=50, description="Жанр видео")
    style: Optional[str] = Field(None, max_length=50, description="Стиль видео")
    time: float = Field(30.0, ge=10, le=180, description="Общая длительность видео в секундах")


class GenerateImages(BaseModel):
    project_id: str = Field(..., description="ID проекта для генерации изображений")


class Scene(BaseModel):
    id: str
    scene_number: int
    action: Optional[str] = None
    dialogue: Optional[str] = None
    voice_over: Optional[str] = None
    visual_prompt: Optional[str] = None

class SceneUpdate(BaseModel):
    scene_number: int = Field(ge = 1, le = 30)
    action: Optional[str] = None
    dialogue: Optional[str] = None
    voice_over: Optional[str] = None
    visual_prompt: Optional[str] = None

class SceneListResponse(BaseModel):
    project_id: str
    scenes: List[Scene]

class SceneUpdateRequest(BaseModel):
    project_id: str
    scenes: List[SceneUpdate]
    