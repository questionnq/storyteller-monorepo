from fastapi import APIRouter, HTTPException
from backend.app.service.script_service import generate_script
from .shemas import ScriptRequest

router = APIRouter(prefix = "/api/v1")

@router.post("/generate-script")
async def generate_script_endpoint(request: ScriptRequest):
    result = await generate_script(request.promt, request.style, request.time)

    if not result:
        raise HTTPException(status_code=500, detail="Script generation failed")
    return result