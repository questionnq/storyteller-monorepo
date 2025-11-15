# Оптимизация для работы с ограничением памяти 512 МБ (Render Free Tier)

## Проблема
Бесплатный план Render ограничивает память до 512 МБ. Предыдущая реализация на MoviePy загружала все видео и изображения в память, вызывая переполнение.

## Решение

### 1. Замена MoviePy на прямой вызов ffmpeg
- **До**: MoviePy держал все клипы в памяти (5-10x больше памяти)
- **После**: ffmpeg обрабатывает видео потоково (в 5-10 раз эффективнее)

### 2. Снижение разрешения
- **До**: 1080x1920 (Full HD вертикальное)
- **После**: 720x1280 (HD вертикальное)
- **Экономия**: ~40% памяти

### 3. Агрессивное сжатие изображений
- **До**: JPEG quality 95, LANCZOS resampling
- **После**: JPEG quality 70, BILINEAR resampling, optimize=True
- **Экономия**: ~50-60% размера файлов

### 4. Явная очистка памяти
- Использование `gc.collect()` после каждой тяжелой операции
- Немедленное удаление объектов после использования (`del`, `.close()`)

### 5. Оптимизация ffmpeg параметров
```bash
-preset ultrafast      # Вместо medium - экономит CPU и память
-crf 28               # Вместо 23 - более агрессивное сжатие
-threads 2            # Ограничение потоков (меньше памяти)
-max_muxing_queue_size 1024  # Уменьшение буфера
```

## Установка ffmpeg на Render

### Вариант 1: Через render.yaml (рекомендуется)
Добавьте в ваш `render.yaml`:
```yaml
services:
  - type: web
    name: your-backend
    env: python
    buildCommand: "apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

### Вариант 2: Через Dockerfile
Создайте `Dockerfile` в папке backend:
```dockerfile
FROM python:3.11-slim

# Устанавливаем ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Вариант 3: Через Build Command в Render Dashboard
В настройках вашего сервиса на Render.com:
```bash
apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
```

## Оптимизация фоновых видео

### Текущие размеры
- `abstract.mp4`: 12 МБ
- `minecraft.mp4`: 33 МБ
- `subway.mp4`: 61 МБ

**ВАЖНО**: Эти файлы слишком большие и должны быть оптимизированы!

### Как оптимизировать
Запустите скрипт (требуется ffmpeg):
```bash
cd backend
bash optimize_backgrounds.sh
mv assets/backgrounds/optimized/*.mp4 assets/backgrounds/
```

Или вручную для каждого видео:
```bash
ffmpeg -i input.mp4 -y \
    -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2" \
    -c:v libx264 \
    -preset ultrafast \
    -crf 28 \
    -maxrate 500k \
    -bufsize 1000k \
    -an \
    -r 24 \
    -t 15 \
    output.mp4
```

**Целевые размеры**: < 2 МБ на файл

## Мониторинг использования памяти

Добавьте в код для отладки:
```python
import psutil
import os

process = psutil.Process(os.getpid())
mem_mb = process.memory_info().rss / 1024 / 1024
print(f"[MEMORY] Current usage: {mem_mb:.2f} MB")
```

## Дополнительные рекомендации

1. **Ограничьте количество одновременных рендеров**: Добавьте очередь задач
2. **Используйте кэширование**: Сохраняйте обработанные изображения
3. **Мониторьте логи Render**: Проверяйте на превышение памяти
4. **Рассмотрите платный план**: Если проблемы продолжаются

## Проверка результатов

После деплоя на Render проверьте логи:
```
[VIDEO_SERVICE] Starting memory-optimized video creation
[VIDEO_SERVICE] Scenes: 5, Duration: 30.0, Background: minecraft
[VIDEO_SERVICE] Processing scene 1/5
[VIDEO_SERVICE] Scene 1 processed and compressed
[FFMPEG] Building video with 5 images
[FFMPEG] Running command: ffmpeg -y -i ...
[FFMPEG] Video built successfully!
```

Если видите ошибку "Killed" - это означает превышение памяти.
