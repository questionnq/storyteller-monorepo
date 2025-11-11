from fastapi import APIRouter, HTTPException, Depends
from app.service.gemini_script import generate_script
from app.service.image_script import generate_image
from .shemas import ScriptRequest
from app.db.supa_request import create_project_with_scenes, get_project, get_project_scenes, get_all_projects, get_scenes_by_project, update_scene_image_url
from app.db.auth import get_current_user


router = APIRouter()

## Generate script endpoint
@router.post("/generate-script")
async def generate_script_endpoint(request: ScriptRequest, 
    user_id: str = Depends(get_current_user)):
    
    result = await generate_script(request.prompt, request.genre, request.style, request.time)
    
    if not result:
        raise HTTPException(status_code=500, detail="Script generation failed")

    ## try to save to database
    try:
        project_id = create_project_with_scenes(
            script=result, 
            user_prompt=request.prompt,
            time=request.time, 
            genre=request.genre, 
            style=request.style,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

    return {
        "project_id": project_id,
        "script": result
    }


## Get all projects for user
@router.get("/projects")
async def get_all_projects_endpoint(user_id: str = Depends(get_current_user)): # ❗ Аутентификация
    # Этот роут необходим для dashboard.vue
    try:
        projects = get_all_projects(user_id) 
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load projects: {str(e)}")


## Get specific project by ID
@router.get("/projects/{project_id}")
async def get_project_endpoint(project_id: str, user_id: str = Depends(get_current_user)):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scenes = get_project_scenes(project_id) or []

    # приводи к той форме, что ожидает фронт
    script = {
        "title": project.get("title") or "Проект",
        "description": project.get("description") or "",
        "intro": project.get("intro") or "",
        "scenes": [
            {
                "scene_number": s.get("scene_number"),
                "action": s.get("action") or "",
                "dialogue": s.get("dialogue") or "",
                "voice_over": s.get("voice_over") or "",
                "visual_prompt": s.get("visual_prompt") or ""
            } for s in scenes
        ]
    }

    return {
        "id": project_id,
        "title": project.get("title"),
        "description": project.get("description"), # Это идея, которую ввел юзер
        "settings": {
            "tone": project.get("tone") or "",     
            "style": project.get("style") or "",   
            "duration": project.get("project_time") or 30 
        },
        "script": script,
        "images": {}
    }


@router.post("/generate-image/{project_id}")
async def generate_images(project_id: str):
    # make response to db
    scenes = get_scenes_by_project(project_id)

    if not scenes:
        raise HTTPException(status_code=404, detail="No scenes found for this project")
    
    result = []

    ## Make and save url for each scene
    for scene in scenes:
        promt = scene.get("visual_prompt")
        image_url = await generate_image(promt)
        update_scene_image_url(scene["id"], image_url)
        result.append({
            "scene_id": scene["id"],
            "promt": promt,
            "generated_image_url": image_url
        })


    return {
        "project_id": project_id,
        "scenes": result
    }