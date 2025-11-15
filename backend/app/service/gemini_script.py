import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import GEMINI_API_KEY
import re
import json

genai.configure(api_key=GEMINI_API_KEY)


async def generate_script(prompt: str | None, genre: str | None, style: str | None, time: float | None) -> dict:
    """Генерация сценария с помощью Gemini API"""

    prompt = f"""
    Ты — профессиональный сценарист, пиарщик и эксперт по созданию вирусного контента для вертикальных платформ (TikTok, YouTube Shorts, Reels).
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

    Дополнительные требования и контекст: Ролик не будет сниматься и монтироваться, это будет слайд-шоу (по сценам) и озвучкой текста, который ты напишешь. Не используй в описании действий динамичные изменения, такие как "камера движется", "ракурс переходит" и т.п., поскольку это будет слайд-шоу. Промпт для ИИ-художника желательно должеен компакто содержать всё самое важное и не превышать около 170 символов. На изображениях не должно быть никакого текста. Если вдруг ты хочешь создать изображение, которое содержит черный фон и текст на нём, то в промпте изображения должен быть просто черный фон, а текст, который хочешь сказать, пиши в "закадровом голосе". Если вдруг ты хочешь написать диалог, то перед фразами персонажей обязательно должно быть вступление в формате "Он сказал:" или другое подобное, подходящее к остальному тексту. Действия в сцене озвучиваться не будут, поэтому в сценарии обязательно хотя бы в одной сцене должен быть закадровый голос. Первая сцена может быть (но необязательно) "хуковая" или "байтовая" в формате Youtube Shorts или TikTok. Не прописывай в Диалогах (если есть) и Закадровой речи текст в скобках, даже для описания интонаций произнесения. Не перебарщивай с количеством текста на одной сцене, поскольку текст всего сценария (закадровый голос + диалоги) нужно будет успеть озвучить за примерно {time} секунд. Не больше!
    

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


    
