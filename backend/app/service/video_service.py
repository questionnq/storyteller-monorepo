"""
Сервис для создания видео из изображений (слайд-шоу) с фоновым видео
Оптимизирован для работы с ограничением памяти 512 МБ
"""
import os
import tempfile
import uuid
import requests
import subprocess
import gc
import json
from typing import List, Dict
from PIL import Image
from app.db.supa_request import supabase


def download_from_supabase_or_url(url: str, file_name_hint: str = None) -> bytes:
    """
    Скачивает файл из Supabase Storage или по прямому URL

    Args:
        url: URL файла (может быть публичный или подписанный)
        file_name_hint: Имя файла в storage (для альтернативного метода)

    Returns:
        bytes: Содержимое файла
    """
    try:
        # Сначала пробуем скачать по URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        # Если не получилось по URL - пробуем через SDK
        if file_name_hint:
            try:
                # Извлекаем имя файла из URL если не передано
                if not file_name_hint and '/videos/' in url:
                    file_name_hint = url.split('/videos/')[-1].split('?')[0]

                # Скачиваем через Supabase SDK
                file_data = supabase.storage.from_("videos").download(file_name_hint)
                return file_data
            except Exception as sdk_error:
                raise Exception(f"Failed to download file: URL method failed ({str(e)}), SDK method failed ({str(sdk_error)})")
        raise Exception(f"Failed to download file from URL: {str(e)}")


# Пути к фоновым видео (абсолютные пути от корня проекта)
import os as _os
# __file__ это G:\site\backend\app\service\video_service.py
# dirname 1 раз: G:\site\backend\app\service
# dirname 2 раза: G:\site\backend\app
# dirname 3 раза: G:\site\backend
_BACKEND_DIR = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

BACKGROUND_VIDEOS = {
    "minecraft": _os.path.join(_BACKEND_DIR, "assets", "backgrounds", "minecraft.mp4"),
    "subway": _os.path.join(_BACKEND_DIR, "assets", "backgrounds", "subway.mp4"),
    "abstract": _os.path.join(_BACKEND_DIR, "assets", "backgrounds", "abstract.mp4"),
}


def get_audio_duration(audio_path: str) -> float:
    """
    Получает длительность аудио файла через ffprobe

    Args:
        audio_path: Путь к аудио файлу

    Returns:
        float: Длительность в секундах
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            audio_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            print(f"[AUDIO_DURATION] Detected audio duration: {duration}s")
            return duration
        else:
            print(f"[AUDIO_DURATION] ffprobe failed, using default 30s")
            return 30.0

    except Exception as e:
        print(f"[AUDIO_DURATION] Error getting duration: {str(e)}, using default 30s")
        return 30.0


async def create_slideshow_video(
    scenes: List[Dict],
    voiceover_url: str = None,
    subtitle_content: str = None,
    total_duration: float = 30.0,
    background_style: str = "minecraft"
) -> str:
    """
    Создает слайд-шоу видео из изображений сцен с фоновым видео
    ОПТИМИЗИРОВАНО для работы с ограничением памяти 512 МБ
    Использует ffmpeg напрямую вместо MoviePy

    Args:
        scenes: Список сцен с generated_image_url
        voiceover_url: URL аудио озвучки (опционально)
        subtitle_content: Содержимое субтитров в формате SRT (опционально)
        total_duration: Общая длительность видео в секундах
        background_style: Стиль фонового видео ('minecraft', 'subway', 'abstract')

    Returns:
        str: Публичный URL загруженного видео
    """
    print(f"[VIDEO_SERVICE] Starting memory-optimized video creation")
    print(f"[VIDEO_SERVICE] Scenes: {len(scenes)}, Duration: {total_duration}, Background: {background_style}")

    temp_files = []

    try:
        # Фильтруем сцены с изображениями
        valid_scenes = [s for s in scenes if s.get("generated_image_url")]
        print(f"[VIDEO_SERVICE] Valid scenes with images: {len(valid_scenes)}")

        if not valid_scenes:
            raise ValueError("No scenes with generated images found")

        # ПРИМЕЧАНИЕ: Длительность будет пересчитана после загрузки аудио
        # Это временное значение для логирования
        duration_per_scene = total_duration / len(valid_scenes)
        print(f"[VIDEO_SERVICE] Initial duration per scene: {duration_per_scene}s")

        # ОПТИМИЗАЦИЯ: Уменьшаем разрешение до 720x1280 (вместо 1080x1920)
        video_width = 720
        video_height = 1280

        # Обрабатываем и сохраняем изображения по одному с агрессивным сжатием
        processed_images = []
        for i, scene in enumerate(valid_scenes):
            print(f"[VIDEO_SERVICE] Processing scene {i+1}/{len(valid_scenes)}")
            image_url = scene.get("generated_image_url")

            # Скачиваем изображение
            print(f"[VIDEO_SERVICE] Downloading image for scene {i+1}...")
            img_content = download_from_supabase_or_url(image_url)
            print(f"[VIDEO_SERVICE] Downloaded {len(img_content)} bytes")

            # Сохраняем во временный файл
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_img.write(img_content)
            temp_img.close()
            temp_files.append(temp_img.name)

            # ОПТИМИЗАЦИЯ: Агрессивно сжимаем изображение
            img = Image.open(temp_img.name)

            # Размещаем картинку в верхней части экрана (60% высоты)
            overlay_height = int(video_height * 0.6)
            overlay_width = int(overlay_height * img.width / img.height)

            # ОПТИМИЗАЦИЯ: Используем BILINEAR вместо LANCZOS (быстрее и меньше памяти)
            img_resized = img.resize((overlay_width, overlay_height), Image.Resampling.BILINEAR)

            # Освобождаем память от оригинального изображения
            img.close()
            del img

            # Сохраняем с агрессивным сжатием (качество 70 вместо 95)
            temp_processed = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            img_resized.save(temp_processed.name, format="JPEG", quality=70, optimize=True)
            temp_processed.close()
            temp_files.append(temp_processed.name)

            processed_images.append({
                "path": temp_processed.name,
                "width": overlay_width,
                "height": overlay_height,
                "start_time": i * duration_per_scene,
                "duration": duration_per_scene
            })

            # Освобождаем память
            img_resized.close()
            del img_resized
            gc.collect()  # Явная очистка памяти

            print(f"[VIDEO_SERVICE] Scene {i+1} processed and compressed")

        # Проверяем наличие фонового видео
        background_path = BACKGROUND_VIDEOS.get(background_style)
        print(f"[VIDEO_SERVICE] Background path: {background_path}")

        if not background_path or not os.path.exists(background_path):
            print(f"[VIDEO_SERVICE] Background video not found, creating black background")
            # Создаем черный фон
            background_path = create_solid_color_image(video_width, video_height, (0, 0, 0))
            temp_files.append(background_path)

        # Скачиваем аудио, если есть
        audio_path = None
        actual_duration = total_duration  # По умолчанию используем переданную длительность

        if voiceover_url:
            print(f"[VIDEO_SERVICE] Downloading voiceover...")
            try:
                audio_content = download_from_supabase_or_url(voiceover_url)
                audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                audio_temp.write(audio_content)
                audio_temp.close()
                audio_path = audio_temp.name
                temp_files.append(audio_path)
                print(f"[VIDEO_SERVICE] Voiceover downloaded: {len(audio_content)} bytes")

                # ВАЖНО: Получаем реальную длительность аудио
                actual_duration = get_audio_duration(audio_path)
                print(f"[VIDEO_SERVICE] Using audio duration: {actual_duration}s (was {total_duration}s)")

                # ПЕРЕСЧИТЫВАЕМ длительность для каждой сцены
                if actual_duration != total_duration:
                    new_duration_per_scene = actual_duration / len(valid_scenes)
                    print(f"[VIDEO_SERVICE] Recalculating scene durations: {new_duration_per_scene}s per scene")

                    for i, img_info in enumerate(processed_images):
                        img_info["start_time"] = i * new_duration_per_scene
                        img_info["duration"] = new_duration_per_scene
                        print(f"[VIDEO_SERVICE] Scene {i+1}: start={img_info['start_time']:.2f}s, duration={img_info['duration']:.2f}s")

                # Освобождаем память
                del audio_content
                gc.collect()
            except Exception as e:
                print(f"[VIDEO_SERVICE] Warning: Could not download voiceover: {str(e)}")
                audio_path = None

        # Сохраняем субтитры во временный файл если есть
        subtitle_path = None
        if subtitle_content:
            print(f"[VIDEO_SERVICE] Saving subtitles to temp file...")
            subtitle_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".srt", mode='w', encoding='utf-8')
            subtitle_temp.write(subtitle_content)
            subtitle_temp.close()
            subtitle_path = subtitle_temp.name
            temp_files.append(subtitle_path)
            print(f"[VIDEO_SERVICE] Subtitles saved to: {subtitle_path}")

        # КЛЮЧЕВАЯ ОПТИМИЗАЦИЯ: Используем ffmpeg напрямую
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_temp.close()
        temp_files.append(output_temp.name)

        print(f"[VIDEO_SERVICE] Building video with ffmpeg...")
        print(f"[VIDEO_SERVICE] Final video duration: {actual_duration}s")
        success = build_video_with_ffmpeg(
            background_path=background_path,
            images=processed_images,
            audio_path=audio_path,
            output_path=output_temp.name,
            video_width=video_width,
            video_height=video_height,
            total_duration=actual_duration,  # Используем реальную длительность!
            subtitle_path=subtitle_path
        )

        if not success:
            raise Exception("FFmpeg video building failed")

        print(f"[VIDEO_SERVICE] Video export complete!")

        # Загружаем в Supabase Storage
        file_name = f"video_{uuid.uuid4()}.mp4"
        print(f"[VIDEO_SERVICE] Uploading video to Supabase: {file_name}")

        with open(output_temp.name, "rb") as f:
            file_data = f.read()
        print(f"[VIDEO_SERVICE] Read {len(file_data)} bytes from exported video")

        # Используем upsert для перезаписи файла
        print(f"[VIDEO_SERVICE] Uploading to Supabase Storage...")
        res = supabase.storage.from_("videos").upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": "video/mp4", "upsert": "true"}
        )
        print(f"[VIDEO_SERVICE] Upload complete!")

        # Освобождаем память от файла
        del file_data
        gc.collect()

        # Получаем публичный URL
        try:
            public_url = supabase.storage.from_("videos").get_public_url(file_name)
            print(f"[VIDEO_SERVICE] Got public URL: {public_url}")
            return public_url
        except Exception as e:
            # Fallback: создаем signed URL на 1 год
            print(f"[VIDEO_SERVICE] get_public_url failed ({str(e)}), falling back to signed URL")
            signed_url = supabase.storage.from_("videos").create_signed_url(
                file_name,
                expires_in=31536000  # 1 год в секундах
            )
            print(f"[VIDEO_SERVICE] Got signed URL: {signed_url['signedURL']}")
            return signed_url['signedURL']

    except Exception as e:
        print(f"[VIDEO_SERVICE] ERROR during video creation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to create video: {str(e)}")

    finally:
        # Очищаем все временные файлы
        print(f"[VIDEO_SERVICE] Cleaning up {len(temp_files)} temporary files...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                    print(f"[VIDEO_SERVICE] Deleted temp file: {temp_file}")
                except Exception as cleanup_error:
                    print(f"[VIDEO_SERVICE] Failed to delete temp file {temp_file}: {str(cleanup_error)}")
        print(f"[VIDEO_SERVICE] Cleanup complete")


def build_video_with_ffmpeg(
    background_path: str,
    images: List[Dict],
    audio_path: str,
    output_path: str,
    video_width: int,
    video_height: int,
    total_duration: float,
    subtitle_path: str = None
) -> bool:
    """
    Собирает видео используя ffmpeg напрямую (экономит память)
    С медленным zoom эффектом, центрированием изображений и субтитрами

    Args:
        background_path: Путь к фоновому видео
        images: Список словарей с информацией об изображениями
        audio_path: Путь к аудио файлу (может быть None)
        output_path: Путь для сохранения результата
        video_width: Ширина финального видео
        video_height: Высота финального видео
        total_duration: Общая длительность
        subtitle_path: Путь к файлу субтитров .srt (может быть None)

    Returns:
        bool: True если успешно, False иначе
    """
    try:
        print(f"[FFMPEG] Building video with {len(images)} images")

        # Строим filter_complex для наложения изображений
        filter_parts = []

        # Базовый фон - обрезаем до нужной длительности и масштабируем
        # stream_loop уже зациклил видео на входе, здесь просто обрезаем и масштабируем
        filter_parts.append(f"[0:v]trim=duration={total_duration},setpts=PTS-STARTPTS,scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2[bg_raw]")

        # Добавляем субтитры НА ФОН (если есть), ДО наложения слайд-шоу
        if subtitle_path:
            # Экранируем путь для ffmpeg
            escaped_subtitle_path = subtitle_path.replace('\\', '/').replace(':', '\\\\:')
            # Субтитры внизу экрана на фоне - с позицией снизу (MarginV=30)
            subtitle_on_bg = f"[bg_raw]subtitles='{escaped_subtitle_path}':force_style='FontName=Arial,FontSize=20,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BackColour=&H80000000&,Bold=1,Outline=2,Shadow=1,Alignment=2,MarginV=30'[bg]"
            filter_parts.append(subtitle_on_bg)
        else:
            # Если нет субтитров - просто переименовываем label
            filter_parts.append(f"[bg_raw]null[bg]")

        # Добавляем каждое изображение с zoom эффектом
        current_base = "bg"
        for i, img_info in enumerate(images):
            img_input_idx = i + 1  # Индексы входов: 0 - фон, 1+ - изображения

            # Позиция Y (центрируем вертикально - в середине экрана)
            # Оставляем место снизу для фона (40% высоты для изображения)
            y_pos = int(video_height * 0.15)  # Начинаем с 15% от верха

            # Позиция X (центрируем по горизонтали)
            x_pos = (video_width - img_info["width"]) // 2

            # Создаем overlay с временными рамками и ZOOM эффектом
            start_time = img_info["start_time"]
            end_time = start_time + img_info["duration"]
            duration = img_info["duration"]

            # Ken Burns эффект (медленный zoom): от 1.0 до 1.15 масштаба
            # zoompan параметры:
            # z - масштаб: 1.0 + (on/продолжительность) * 0.15 = плавный zoom от 1.0 до 1.15
            # d - длительность в кадрах
            # s - размер выходного кадра
            # fps - кадровая частота
            total_frames = int(duration * 24)
            zoom_filter = f"[{img_input_idx}:v]scale={img_info['width']}:{img_info['height']},zoompan=z='min(1.0+on/{total_frames}*0.15,1.15)':d={total_frames}:s={img_info['width']}x{img_info['height']}:fps=24[img{i}]"
            filter_parts.append(zoom_filter)

            if i < len(images) - 1:
                # Промежуточный результат
                output_label = f"tmp{i}"
                filter_parts.append(
                    f"[{current_base}][img{i}]overlay={x_pos}:{y_pos}:enable='between(t,{start_time},{end_time})'[{output_label}]"
                )
                current_base = output_label
            else:
                # Последний overlay - всегда выходной label
                filter_parts.append(
                    f"[{current_base}][img{i}]overlay={x_pos}:{y_pos}:enable='between(t,{start_time},{end_time})'[outv]"
                )

        filter_complex = ";".join(filter_parts)
        print(f"[FFMPEG] Filter complex length: {len(filter_complex)} chars")
        print(f"[FFMPEG] Filter preview: {filter_complex[:300]}...")  # Показываем первые 300 символов

        # Строим команду ffmpeg
        cmd = ["ffmpeg", "-y"]  # -y для перезаписи

        # Входы: фон + все изображения + аудио (ВСЕ ВХОДЫ ДОЛЖНЫ БЫТЬ ДО ФИЛЬТРОВ!)
        # ВАЖНО: stream_loop -1 для бесконечного зацикливания фонового видео
        cmd.extend(["-stream_loop", "-1", "-i", background_path])
        for img_info in images:
            cmd.extend(["-i", img_info["path"]])

        # Добавляем аудио input если есть (ПЕРЕД filter_complex!)
        audio_input_index = None
        if audio_path:
            audio_input_index = len(images) + 1  # Индекс аудио = фон(0) + изображения(N) + 1
            cmd.extend(["-i", audio_path])

        # Фильтр (ПОСЛЕ всех входов)
        cmd.extend(["-filter_complex", filter_complex])

        # Маппинг видео
        cmd.extend(["-map", "[outv]"])

        # Маппинг аудио если есть
        if audio_input_index is not None:
            cmd.extend(["-map", f"{audio_input_index}:a"])
            cmd.extend(["-c:a", "aac", "-b:a", "128k"])

        # ОПТИМИЗАЦИИ для экономии памяти и CPU:
        cmd.extend([
            "-c:v", "libx264",           # Видео кодек
            "-preset", "ultrafast",       # КРИТИЧНО: ultrafast вместо medium (экономит CPU и память)
            "-crf", "28",                 # Более высокое сжатие (23 по умолчанию, 28 = меньше размер)
            "-movflags", "+faststart",    # Для веб-стриминга
            "-pix_fmt", "yuv420p",        # Совместимость
            "-r", "24",                   # FPS
            "-t", str(total_duration),    # Длительность
            "-threads", "2",              # КРИТИЧНО: ограничиваем потоки до 2 (меньше памяти)
            "-max_muxing_queue_size", "1024",  # Уменьшаем буфер
            output_path
        ])

        print(f"[FFMPEG] Running command: {' '.join(cmd[:10])}... (truncated)")

        # Запускаем ffmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300  # 5 минут таймаут
        )

        if result.returncode != 0:
            error_output = result.stderr.decode('utf-8', errors='ignore')
            print(f"[FFMPEG] ERROR: {error_output[-500:]}")  # Последние 500 символов ошибки
            return False

        print(f"[FFMPEG] Video built successfully!")
        return True

    except subprocess.TimeoutExpired:
        print(f"[FFMPEG] ERROR: Process timeout (> 5 minutes)")
        return False
    except Exception as e:
        print(f"[FFMPEG] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_solid_color_image(width: int, height: int, color: tuple) -> str:
    """
    Создает изображение сплошного цвета и возвращает путь к временному файлу

    Args:
        width: Ширина изображения
        height: Высота изображения
        color: RGB цвет (r, g, b)

    Returns:
        str: Путь к временному файлу
    """
    img = Image.new('RGB', (width, height), color)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    img.save(temp_file.name, quality=95)
    temp_file.close()
    return temp_file.name


# Функции для субтитров удалены, так как они зависели от MoviePy
# В будущем субтитры можно добавить через ffmpeg filter (drawtext или subtitles)
