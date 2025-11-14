import urllib.parse
import requests
import time
import asyncio

# Список API для генерации изображений (в порядке приоритета)
IMAGE_APIS = [
    {
        "name": "Pollinations (Flux)",
        "url_template": "https://image.pollinations.ai/prompt/{prompt}?width=768&height=1024&nologo=true&model=flux",
        "timeout": 15
    },
    {
        "name": "Pollinations (Turbo)",
        "url_template": "https://image.pollinations.ai/prompt/{prompt}?width=768&height=1024&nologo=true&model=turbo",
        "timeout": 10
    },
    {
        "name": "Replicate Flux Schnell",
        "url_template": "https://replicate.delivery/pbxt/dummyid/out.png?prompt={prompt}",
        "timeout": 10
    }
]


async def generate_image(visual_promt: str, max_retries: int = 2):
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

        # Кодируем промпт
        encoded_prompt = urllib.parse.quote(visual_promt)
        url = api_config["url_template"].format(prompt=encoded_prompt)

        print(f"[IMAGE_GEN] URL: {url[:120]}...")

        # Пробуем несколько раз для текущего API
        for attempt in range(max_retries):
            try:
                print(f"[IMAGE_GEN] Attempt {attempt + 1}/{max_retries}...")

                # Просто пробуем GET запрос с таймаутом
                response = requests.get(url, timeout=api_config["timeout"], stream=True)

                if response.status_code == 200:
                    # Проверяем что это действительно изображение
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type or len(response.content) > 1000:
                        print(f"[IMAGE_GEN] ✓ Success with {api_name}!")
                        return url
                    else:
                        print(f"[IMAGE_GEN] Response is not an image, trying next...")
                        break

                elif response.status_code in [530, 502, 503, 504]:
                    print(f"[IMAGE_GEN] Server error {response.status_code}, waiting...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
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
    print(f"[IMAGE_GEN] ⚠ All APIs failed, using placeholder")
    return await generate_placeholder_image(visual_promt)


async def generate_placeholder_image(visual_promt: str):
    """
    Генерирует placeholder изображение с текстом промпта
    """
    # Берем первые слова промпта для текста
    short_text = visual_promt[:50].replace(' ', '+')

    # Используем placeholder сервис
    placeholder_url = f"https://placehold.co/768x1024/2d2d2d/white?text={short_text}"

    print(f"[IMAGE_GEN] Placeholder URL: {placeholder_url}")
    return placeholder_url