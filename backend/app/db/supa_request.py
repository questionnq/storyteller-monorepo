from supabase import create_client
from datetime import datetime
import uuid
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

## Add scene in project
def create_project_with_scenes(script: dict, user_id: str = None) -> str:
    # 1️⃣ Создаём проект
    project_data = {
        "user_id": user_id,
        "title": script.get("title"),
        "description": script.get("intro"),  # intro → description
        "render_status": "pending"  # можно по умолчанию
    }

    res = supabase.table("projects").insert(project_data).execute()
    

    project_id = res.data[0]["id"]

    # 2️⃣ Создаём сцены
    scenes_data = []
    for scene in script.get("scenes", []):
        text_content = f"{scene.get('description','')}\n{scene.get('dialogue','')}"
        scenes_data.append({
            "project_id": project_id,
            "scene_number": scene.get("scene_number"),
            "text": text_content,
            "visual_prompt": scene.get("description")  # если хочешь
        })

    if scenes_data:
        res_scenes = supabase.table("scenes").insert(scenes_data).execute()
        if res_scenes.error:
            raise Exception(f"Supabase insert scenes error: {res_scenes.error.message}")

    return project_id

 

## Get project by id
def get_project_by_id(project_id: str):
    return {0}