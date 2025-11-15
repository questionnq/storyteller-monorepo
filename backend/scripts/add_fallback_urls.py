"""
Скрипт для добавления URL фоллбэк-изображений в таблицу fallback_images.

Использование:
    python scripts/add_fallback_urls.py
"""

import sys
from pathlib import Path

# Добавляем корневую папку в путь для импорта
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.supa_request import supabase

# Список URL фоллбэк-изображений (768x1024, вертикальные)
# Источники: Unsplash, Pexels (бесплатные стоковые)
FALLBACK_IMAGE_URLS = [
    {
        "url": "https://avatars.mds.yandex.net/i?id=c6366f7e56c0cab815e9bdb38cb80352d09ef9b6-5657852-images-thumbs&n=13",
        "description": "Chill guy",
        "category": "nature"
    },
    {
        "url": "https://avatars.mds.yandex.net/i?id=3f83e7e90b5ceb9770a266b7642a1d0e03372323-8498042-images-thumbs&n=13",
        "description": "Minimal pink gradient",
        "category": "general"
    },
    {
        "url": "https://avatars.mds.yandex.net/i?id=1860d1837f3684c95f928998a79104e60666913e-5340698-images-thumbs&n=13",
        "description": "Jocker",
        "category": "abstract"
    },
    {
        "url": "https://avatars.mds.yandex.net/i?id=dbc35d11d7fb459f7d14fe27cf54ebc0e1387d1c-6557067-images-thumbs&n=13",
        "description": "Watercolor texture soft",
        "category": "texture"
    },
    {
        "url": "https://avatars.mds.yandex.net/i?id=faa09aca5d2d230f2077fd615135c679ac7cc2bc-12542812-images-thumbs&n=13",
        "description": "Bokeh light background",
        "category": "abstract"
    },
    {
        "url": "https://avatars.mds.yandex.net/i?id=98a7f18a881af33dada0c6f8f86926bf0c12c11a-7758299-images-thumbs&n=13",
        "description": "Sky clouds dreamy",
        "category": "nature"
    },
    {
        "url": "https://i.ytimg.com/vi/9W6g43heods/maxresdefault.jpg",
        "description": "Mountain landscape vertical",
        "category": "nature"
    },
    {
        "url": "https://i.pinimg.com/736x/1c/da/e6/1cdae676b88b08b80dcd6f5c7854759a.jpg",
        "description": "Car vintage aesthetic",
        "category": "general"
    },
]


def add_fallback_urls():
    """Добавляет URL фоллбэк-изображений в таблицу fallback_images"""

    print("\n" + "="*60)
    print("🚀 Добавление фоллбэк-изображений в базу данных")
    print("="*60 + "\n")

    # Очищаем старые записи
    try:
        result = supabase.table("fallback_images").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Старые записи удалены из таблицы fallback_images\n")
    except Exception as e:
        print(f"⚠️  Ошибка очистки таблицы: {e}\n")

    # Добавляем новые URL
    added_count = 0
    for idx, image_data in enumerate(FALLBACK_IMAGE_URLS, 1):
        try:
            print(f"📤 [{idx}/{len(FALLBACK_IMAGE_URLS)}] Добавляю: {image_data['description']}...")

            supabase.table("fallback_images").insert({
                "image_url": image_data["url"],
                "category": image_data["category"],
                "description": image_data["description"],
                "is_active": True
            }).execute()

            print(f"   ✅ URL: {image_data['url'][:60]}...\n")
            added_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка: {e}\n")

    print(f"\n{'='*60}")
    print(f"✅ Добавлено: {added_count}/{len(FALLBACK_IMAGE_URLS)} изображений")
    print(f"{'='*60}\n")

    # Проверяем что добавилось
    try:
        result = supabase.table("fallback_images").select("*").eq("is_active", True).execute()
        print(f"\n📊 Всего активных фоллбэков в базе: {len(result.data)}\n")
    except Exception as e:
        print(f"⚠️  Ошибка проверки: {e}\n")


if __name__ == "__main__":
    add_fallback_urls()
