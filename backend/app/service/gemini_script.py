import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import GEMINI_API_KEY
import re
import json

genai.configure(api_key=GEMINI_API_KEY)


async def generate_script(prompt: str | None, genre: str | None, style: str | None, time: float | None) -> dict:
    """Генерация сценария с помощью Gemini API"""

    prompt = f"""
    Ты — профессиональный сценарист и эксперт по созданию вирусного контента для вертикальных платформ (TikTok, YouTube Shorts, Reels).
    Сгенерируй JSON со сценарием для вертикального видео на тему: "{prompt}".
    Жанр видео должен быть: {genre}.
    Стиль видео должен быть: {style}.
    Длительность видео должна быть около {time} секунд.
    Формат JSON должен быть следующим:
    {{
        "title": "Название",
        "intro": "Небольшое вступление",
        "scenes": [
            {{
                "scene_number": 1,
                "action": "Описание действия (что происходит на экране)",
                "dialogue": "Диалог персонажей (если есть, иначе пустая строка)",
                "voice_over": "Текст за кадром (если есть, иначе пустая строка)",
                "visual_prompt": "Детальный промпт для ИИ-художника (на английском)"
            }},
            {{
                "scene_number": 2,
                "action": "Описание действия (что происходит на экране)",
                "dialogue": "Диалог персонажей (если есть, иначе пустая строка)",
                "voice_over": "Текст за кадром (если есть, иначе пустая строка)",
                "visual_prompt": "Детальный промпт для ИИ-художника (на английском)"
            }}
            (... и другие сцены)
        ]
    }}

    

    {f"Стиль видео: {style}." if style else ""}
    """

    safety_settings = [
        {
            "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
            "threshold": HarmBlockThreshold.BLOCK_NONE, 
        },
        {
            "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            "threshold": HarmBlockThreshold.BLOCK_NONE,
        },
        {
            "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            "threshold": HarmBlockThreshold.BLOCK_NONE,
        },
        {
            "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            "threshold": HarmBlockThreshold.BLOCK_NONE,
        },
    ]

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = await model.generate_content_async(prompt,
        safety_settings=safety_settings)

    # Убираем обёртку ```json ... ```
    clean_text = re.sub(r"^```json\s*|\s*```$", "", response.text.strip(), flags=re.MULTILINE)

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": response.text}


    
