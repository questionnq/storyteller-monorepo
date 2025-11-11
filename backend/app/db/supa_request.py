from supabase import create_client
from datetime import datetime
import uuid
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


### ADD PROJECT WITH SCENES
def create_project_with_scenes(script: dict, time: float, genre: str | None, style: str | None) -> str:
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1️⃣ Создаем проект
    project_data = {
        "title": script.get("title"),
        "intro": script.get("intro"),
        "project_time": time,
        "created_at": formatted_time,
        "tone": genre,  
        "style": style
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



    