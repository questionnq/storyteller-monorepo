from supabase import create_client
from datetime import datetime
import uuid
from typing import List
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


###ADD PROJECT WITH SCENES
def create_project_with_scenes(script: dict, user_prompt: str, time: float, genre: str | None, style: str | None, user_id: str) -> str:
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #Создаем проект
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

    #Создаём сцену
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

#Get project by ID and add cache
def get_project(project_id: str):
    res = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    return res.data

#Get scenes by project ID and add cache
def get_project_scenes(project_id: str):
    res = supabase.table("scenes").select("*").eq("project_id", project_id).order("scene_number").execute()
    return res.data


#Get all projects by user ID and add cache
def get_all_projects(user_id: str) -> List[dict]:
    res = supabase.table("projects")\
        .select("id, title, description, created_at, project_time, tone, style")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True).execute()
    return res.data

#Get scenes by project ID
def get_visual_promt_by_project(project_id: str):
    res = supabase.table("scenes").select("id, visual_prompt").eq("project_id", project_id).execute()
    return res.data

#Update scene with generated image URL
def update_scene_image_url(scene_id: str, image_url: str):
    res = supabase.table("scenes").update({"generated_image_url": image_url}).eq("id", scene_id).execute()
    return res.data


def get_scenes_by_project(project_id: str):
    """
    Возвращает все сцены проекта из таблицы 'scenes' по project_id.
    """
    try:
        res = supabase.table("scenes") \
            .select("id, scene_number, action, dialogue, voice_over, visual_prompt") \
            .eq("project_id", project_id) \
            .order("scene_number", desc=False) \
            .execute()

        if not res.data:
            return []  #если сцен нет — возвращаем пустой список

        return res.data

    except Exception as e:
        raise RuntimeError(f"Failed to fetch scenes: {str(e)}")
    
#Get count of scenes in project
def update_scene(project_id: str, scene_number: int, update_data: dict):
    try:
        res = supabase.table("scenes") \
            .update(update_data) \
            .eq("project_id", project_id) \
            .eq("scene_number", scene_number) \
            .execute()

        if not res.data:
            raise ValueError(f"Scene {scene_number} not found for project {project_id}")

        return res.data[0]  #возвращаем обновлённую строку

    except Exception as e:
        raise RuntimeError(f"Database update failed: {str(e)}")
    
##Delete project by ID
def delete_project_by_id(project_id: str):
    try:
        #Удаляем сцены, связанные с проектом
        supabase.table("scenes").delete().eq("project_id", project_id).execute()

        #Удаляем сам проект
        res = supabase.table("projects").delete().eq("id", project_id).execute()

        return res.data

    except Exception as e:
        raise RuntimeError(f"Failed to delete project: {str(e)}")


#Update voiceover URL for project
def update_voiceover_url(project_id: str, voiceover_url: str):
    """Обновляет URL озвучки для проекта"""
    res = supabase.table("projects").update({"voiceover_url": voiceover_url}).eq("id", project_id).execute()
    return res.data


#Update subtitle URL for project
def update_subtitle_url(project_id: str, subtitle_url: str):
    """Обновляет URL субтитров для проекта"""
    res = supabase.table("projects").update({"subtitle_url": subtitle_url}).eq("id", project_id).execute()
    return res.data


#Update project time (duration)
def update_project_time(project_id: str, project_time: float):
    """Обновляет длительность проекта в секундах"""
    res = supabase.table("projects").update({"project_time": project_time}).eq("id", project_id).execute()
    return res.data


#Get random fallback image
def get_random_fallback_image():
    """Получает случайное фоллбэк изображение из базы данных"""
    import random

    try:
        res = supabase.table("fallback_images").select("*").eq("is_active", True).execute()

        if res.data and len(res.data) > 0:
            random_image = random.choice(res.data)
            print(f"[FALLBACK] Selected random image: {random_image.get('description', 'No description')}")
            return random_image.get("image_url")
        else:
            print(f"[FALLBACK] No fallback images found in database")
            return None
    except Exception as e:
        print(f"[FALLBACK] Error getting fallback image: {str(e)}")
        return None


#Update final video URL for project
def update_final_video_url(project_id: str, final_video_url: str):
    """Обновляет URL финального видео для проекта"""
    res = supabase.table("projects").update({"final_video_url": final_video_url}).eq("id", project_id).execute()
    return res.data


#Update render status for project
def update_render_status(project_id: str, status: str):
    """Обновляет статус рендера для проекта

    Возможные статусы: 'pending', 'generating_audio', 'rendering_video', 'completed', 'error'
    """
    res = supabase.table("projects").update({"render_status": status}).eq("id", project_id).execute()
    return res.data


#Get project with voiceover and video data
def get_project_render_data(project_id: str):
    """Получает данные проекта для рендеринга (включая URLs озвучки и видео)"""
    res = supabase.table("projects").select(
        "id, voiceover_url, subtitle_url, final_video_url, render_status, project_time"
    ).eq("id", project_id).single().execute()
    return res.data
