from fastapi import APIRouter, HTTPException
from app.service.script_service import generate_script
from .shemas import ScriptRequest
from app.db.supa_request import create_project_with_scenes, get_project_by_id


router = APIRouter(prefix = "/api/v1")

@router.post("/generate-script")
async def generate_script_endpoint(request: ScriptRequest):
    
    result = await generate_script(request.prompt, request.genre, request.style, request.time)
    
    if not result:
        raise HTTPException(status_code=500, detail="Script generation failed")

    ## try to save to database
    try:
        project_id = create_project_with_scenes(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

    return {
        "project_id": project_id,
        "script": result
    }