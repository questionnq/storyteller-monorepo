from supabase import create_client
from datetime import datetime
import uuid
from typing import List
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


### ADD PROJECT WITH SCENES
def create_project_with_scenes(script: dict, user_prompt: str, time: float, genre: str | None, style: str | None, user_id: str) -> str:
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1️⃣ Создаем проект
    project_data = {
        "title": script.get("title"),
        "description": user_prompt,
        "intro": script.get("intro"),
        "project_time": time,
        "created_at": formatted_time,
        "tone": genre,  
        "style": style,
        "user_id": user_id
    }

    res = supabase.table("projects").insert(project_data).execute()


    
    project_id = res.data[0]["id"]

    # 2️⃣ Создаём сцену
    scenes_data = []
    for scene in script.get("scenes", []):
        scenes_data.append({
            "project_id": project_id,
            "scene_number": scene.get("scene_number"),
            "action": scene.get("action"),
            "dialogue": scene.get("dialogue"),
            "voice_over": scene.get("voice_over"),
            "visual_prompt": scene.get("visual_prompt"),
            "generated_image_url": None,
            "created_at": formatted_time,
        })


    if scenes_data:
        res_scenes = supabase.table("scenes").insert(scenes_data).execute()

    return project_id


def get_project(project_id: str):
    res = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    return res.data

def get_project_scenes(project_id: str):
    res = supabase.table("scenes").select("*").eq("project_id", project_id).order("scene_number").execute()
    return res.data

def get_all_projects(user_id: str) -> List[dict]:
    res = supabase.table("projects")\
        .select("id, title, description, created_at, project_time, tone, style")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True).execute()
    return res.data

## Get scenes by project ID
def get_scenes_by_project(project_id: str):
    response = supabase.table("scenes").select("id, visual_prompt").eq("project_id", project_id).execute()
    return response.data

## Update scene with generated image URL
def update_scene_image_url(scene_id: str, image_url: str):
    res = supabase.table("scenes").update({"generated_image_url": image_url}).eq("id", scene_id).execute()
    return res.data