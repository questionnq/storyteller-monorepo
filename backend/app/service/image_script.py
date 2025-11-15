import urllib.parse
import requests
import time
import asyncio
import io
import base64
from PIL import Image
from app.db.supa_request import supabase
from app.config import HUGGING_FACE_API_KEY
import uuid

# Hugging Face API endpoint для генерации изображений
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

# Глобальный флаг для отслеживания rate limit HF (сбрасывается при перезапуске сервера)
_HF_RATE_LIMITED = False

# Список API для генерации изображений (в порядке приоритета)
IMAGE_APIS = [
    {
        "name": "Hugging Face FLUX Schnell",
        "type": "huggingface",
        "timeout": 30
    },
    {
        "name": "Pollinations (Turbo)",
        "url_template": "https://image.pollinations.ai/prompt/{prompt}?width=768&height=1024&nologo=true&model=turbo",
        "timeout": 45  # Увеличен с 10 до 45 секунд
    },
    {
        "name": "Pollinations (Flux)",
        "url_template": "https://image.pollinations.ai/prompt/{prompt}?width=768&height=1024&nologo=true&model=flux",
        "timeout": 60  # Flux модель медленнее но качественнее
    },
    {
        "name": "Replicate Stable Diffusion",
        "url_template": "https://api.replicate.com/v1/predictions",
        "type": "replicate",
        "timeout": 45
    }
]


async def generate_with_huggingface(prompt: str, timeout: int = 30):
    """
    Генерирует изображение через Hugging Face Inference API
    Загружает результат в Supabase Storage и возвращает публичный URL
    """
    global _HF_RATE_LIMITED

    # Если уже получили rate limit - сразу пропускаем
    if _HF_RATE_LIMITED:
        print(f"[HF] Skipping due to previous rate limit")
        return "SKIP"

    try:
        print(f"[HF] Sending request to Hugging Face...")

        # Делаем POST запрос к Hugging Face API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {HUGGING_FACE_API_KEY}"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 768,
                "height": 1024,
                "num_inference_steps": 4  # Schnell модель работает с 4 шагами
            }
        }

        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=timeout
        )

        if response.status_code == 200:
            # Получили изображение в байтах
            image_bytes = response.content
            print(f"[HF] ✓ Image generated! Size: {len(image_bytes)} bytes")

            # Загружаем в Supabase Storage
            file_name = f"generated_{uuid.uuid4()}.png"

            supabase.storage.from_("videos").upload(
                path=file_name,
                file=image_bytes,
                file_options={"content-type": "image/png", "upsert": "true"}
            )

            # Получаем публичный URL
            public_url = supabase.storage.from_("videos").get_public_url(file_name)
            print(f"[HF] ✓ Uploaded to Supabase: {public_url}")

            return public_url

        elif response.status_code == 503:
            # Модель загружается (нужно подождать)
            print(f"[HF] Model is loading, estimated time: 20s")
            await asyncio.sleep(20)
            return None  # Вернет None для retry
        elif response.status_code == 402:
            # Rate limit / токены закончились
            _HF_RATE_LIMITED = True  # Устанавливаем флаг
            print(f"[HF] Rate limit exceeded (токены закончились), пропускаем HF API для всех последующих запросов")
            return "SKIP"  # Специальный код для пропуска этого API
        else:
            print(f"[HF] Error {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"[HF] Exception: {str(e)}")
        return None


async def generate_image(visual_promt: str, max_retries: int = 3):
    """
    Генерирует изображение, пробуя несколько API в порядке приоритета

    Args:
        visual_promt: Текстовый промпт для генерации
        max_retries: Максимальное количество попыток на API

    Returns:
        str: URL сгенерированного изображения
    """
    # Сокращаем промпт если он слишком длинный
    original_prompt = visual_promt
    if len(visual_promt) > 180:
        visual_promt = visual_promt[:160] + "... vertical, cinematic"
        print(f"[IMAGE_GEN] Prompt shortened from {len(original_prompt)} to {len(visual_promt)} chars")

    # Пробуем каждый API по очереди
    for api_index, api_config in enumerate(IMAGE_APIS):
        api_name = api_config["name"]
        print(f"\n[IMAGE_GEN] Trying API {api_index + 1}/{len(IMAGE_APIS)}: {api_name}")

        # Пробуем несколько раз для текущего API
        for attempt in range(max_retries):
            try:
                print(f"[IMAGE_GEN] Attempt {attempt + 1}/{max_retries}...")

                # Hugging Face API (загружает в Storage)
                if api_config.get("type") == "huggingface":
                    result = await generate_with_huggingface(visual_promt, api_config["timeout"])
                    if result == "SKIP":
                        print(f"[IMAGE_GEN] Skipping {api_name} (rate limit)")
                        break  # Пропускаем этот API полностью
                    elif result:
                        print(f"[IMAGE_GEN] ✓ Success with {api_name}!")
                        return result
                    else:
                        print(f"[IMAGE_GEN] HF returned None, retrying...")
                        await asyncio.sleep(5)
                        continue

                # URL-based APIs (Pollinations и др.)
                else:
                    encoded_prompt = urllib.parse.quote(visual_promt)
                    url = api_config["url_template"].format(prompt=encoded_prompt)
                    print(f"[IMAGE_GEN] URL: {url[:120]}...")

                    response = requests.get(url, timeout=api_config["timeout"], stream=True)

                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type or len(response.content) > 1000:
                            print(f"[IMAGE_GEN] ✓ Success with {api_name}!")
                            return url
                        else:
                            print(f"[IMAGE_GEN] Response is not an image, trying next...")
                            break

                    elif response.status_code in [530, 502, 503, 504]:
                        print(f"[IMAGE_GEN] Server error {response.status_code}, waiting...")
                        await asyncio.sleep(2 ** attempt)
                    else:
                        print(f"[IMAGE_GEN] Status {response.status_code}, trying next API...")
                        break

            except requests.exceptions.Timeout:
                print(f"[IMAGE_GEN] Timeout after {api_config['timeout']}s")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    break

            except requests.exceptions.RequestException as e:
                print(f"[IMAGE_GEN] Request error: {str(e)[:100]}")
                break

    # Если все API провалились - возвращаем placeholder
    print(f"[IMAGE_GEN] ⚠️ All APIs failed, using placeholder")
    return await generate_placeholder_image(visual_promt)


async def generate_placeholder_image(visual_promt: str):
    """
    Возвращает случайное фоллбэк-изображение из базы данных.
    Если в базе нет изображений - возвращает placehold.co
    """
    from app.db.supa_request import get_random_fallback_image

    # Пробуем получить случайное изображение из базы
    fallback_url = get_random_fallback_image()

    if fallback_url:
        print(f"[IMAGE_GEN] Using fallback image from database: {fallback_url[:60]}...")
        return fallback_url

    # Если в базе нет изображений - используем старый placeholder
    print(f"[IMAGE_GEN] ⚠️ No fallback images in database, using placehold.co")
    short_text = visual_promt[:50].replace(' ', '+')
    placeholder_url = f"https://placehold.co/768x1024/2d2d2d/white?text={short_text}"

    print(f"[IMAGE_GEN] Placeholder URL: {placeholder_url}")
    return placeholder_url