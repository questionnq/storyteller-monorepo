import google.generativeai as genai
from app.config import GEMINI_API_KEY
import re
import json

genai.configure(api_key=GEMINI_API_KEY)


async def generate_script(prompt: str | None, genre: str | None, style: str | None, time: float | None) -> dict:
    """Генерация сценария с помощью Gemini API"""

    prompt = f"""
    Сгенерируй JSON с сценарием для видео на тему: "{prompt}".
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
                "description": "Описание сцены",
                "dialogue": "Диалог или текст для сцены"
            }},
            {{
                "scene_number": 2,
                "description": "Описание сцены",
                "dialogue": "Диалог или текст для сцены"
            }}
        ]
    }}

    {f"Стиль видео: {style}." if style else ""}
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = await model.generate_content_async(prompt)

    # Убираем обёртку ```json ... ```
    clean_text = re.sub(r"^```json\s*|\s*```$", "", response.text.strip(), flags=re.MULTILINE)

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": response.text}
