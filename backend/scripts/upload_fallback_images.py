"""
Скрипт для загрузки фоллбэк-изображений в Supabase Storage.

Использование:
1. Поместите изображения (768x1024, вертикальные) в папку backend/assets/fallback_images/
2. Запустите: python scripts/upload_fallback_images.py

Скрипт:
- Загрузит все изображения из backend/assets/fallback_images/ в Supabase Storage (bucket: videos)
- Обновит таблицу fallback_images с реальными URL
"""

import os
import sys
from pathlib import Path

# Добавляем корневую папку в путь для импорта
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.supa_request import supabase

# Папка с фоллбэк-изображениями
FALLBACK_IMAGES_DIR = backend_dir / "assets" / "fallback_images"


def upload_fallback_images():
    """Загружает все изображения из папки fallback_images в Supabase Storage"""

    if not FALLBACK_IMAGES_DIR.exists():
        print(f"❌ Папка {FALLBACK_IMAGES_DIR} не найдена!")
        print(f"Создайте папку и поместите туда изображения (формат: 768x1024, вертикальные)")
        return

    # Получаем список изображений
    image_files = list(FALLBACK_IMAGES_DIR.glob("*.png")) + \
                  list(FALLBACK_IMAGES_DIR.glob("*.jpg")) + \
                  list(FALLBACK_IMAGES_DIR.glob("*.jpeg"))

    if not image_files:
        print(f"❌ Нет изображений в папке {FALLBACK_IMAGES_DIR}")
        print(f"Поддерживаемые форматы: .png, .jpg, .jpeg")
        return

    print(f"\n🖼️  Найдено {len(image_files)} изображений для загрузки\n")

    # Очищаем старые записи в таблице
    try:
        supabase.table("fallback_images").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Старые записи удалены из таблицы fallback_images\n")
    except Exception as e:
        print(f"⚠️  Ошибка очистки таблицы: {e}\n")

    # Загружаем каждое изображение
    uploaded_count = 0
    for image_file in image_files:
        try:
            print(f"📤 Загружаю: {image_file.name}...")

            # Читаем файл
            with open(image_file, "rb") as f:
                image_data = f.read()

            # Генерируем имя файла для Storage
            file_ext = image_file.suffix
            storage_filename = f"fallback_{image_file.stem}{file_ext}"

            # Загружаем в Supabase Storage (bucket: videos)
            supabase.storage.from_("videos").upload(
                path=storage_filename,
                file=image_data,
                file_options={
                    "content-type": f"image/{file_ext[1:]}",
                    "upsert": "true"
                }
            )

            # Получаем публичный URL
            public_url = supabase.storage.from_("videos").get_public_url(storage_filename)

            # Добавляем запись в таблицу fallback_images
            supabase.table("fallback_images").insert({
                "image_url": public_url,
                "category": "general",
                "description": f"Fallback image from {image_file.name}",
                "is_active": True
            }).execute()

            print(f"   ✅ Загружено: {public_url[:60]}...\n")
            uploaded_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка загрузки {image_file.name}: {e}\n")

    print(f"\n{'='*60}")
    print(f"✅ Загрузка завершена: {uploaded_count}/{len(image_files)} изображений")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Загрузка фоллбэк-изображений в Supabase")
    print("="*60 + "\n")

    upload_fallback_images()
