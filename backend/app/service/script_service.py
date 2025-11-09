import google.generativeai as genai
from backend.app.config import GEMINI_API_KEY
import re
import json

genai.configure(api_key=GEMINI_API_KEY)
print("Gemini API Key loaded:", GEMINI_API_KEY)

async def generate_script(promt: str | None, style: str | None, time: float | None) -> dict:
    """Генерация сценария с помощью Gemini API"""

    promt = f"""
    Сгенерируй JSON с сценарием для видео на тему: "{promt}".
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
    response = await model.generate_content_async(promt)

    # Убираем обёртку ```json ... ```
    clean_text = re.sub(r"^```json\s*|\s*```$", "", response.text.strip(), flags=re.MULTILINE)

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": response.text}
