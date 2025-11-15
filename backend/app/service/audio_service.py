"""
Сервис для генерации озвучки (TTS) и субтитров
"""
import os
import tempfile
import uuid
from gtts import gTTS
from app.db.supa_request import supabase
import subprocess
import json

# Для Render.com: используем статические бинарники ffmpeg из imageio-ffmpeg
try:
    import imageio_ffmpeg
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"[AUDIO] Using imageio-ffmpeg binary: {FFMPEG_BINARY}")
except ImportError:
    # Локальная разработка - используем системные
    FFMPEG_BINARY = "ffmpeg"
    print(f"[AUDIO] Using system ffmpeg")


async def generate_voiceover(text: str, lang: str = "ru", speed: float = 1.3) -> str:
    """
    Генерирует озвучку из текста с помощью Google TTS
    После генерации увеличивает скорость с помощью ffmpeg

    Args:
        text: Текст для озвучки
        lang: Язык озвучки (по умолчанию 'ru')
        speed: Множитель скорости (1.0 = нормальная, 1.3 = на 30% быстрее)

    Returns:
        str: Публичный URL загруженного аудио файла
    """
    try:
        # Генерируем аудио с помощью gTTS
        # Используем tld='com.au' для более приятного женского голоса
        tts = gTTS(text=text, lang=lang, slow=False, tld='com.au')

        # Создаем временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        # Сохраняем аудио во временный файл
        tts.save(temp_path)

        # Если нужна другая скорость - обрабатываем через ffmpeg
        final_audio_path = temp_path
        if speed != 1.0:
            import subprocess

            # Создаем еще один временный файл для ускоренного аудио
            speed_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            speed_temp_path = speed_temp.name
            speed_temp.close()

            # Используем atempo фильтр для изменения скорости без изменения тона
            # atempo может работать только в диапазоне 0.5-2.0
            atempo_value = min(max(speed, 0.5), 2.0)

            ffmpeg_cmd = [
                FFMPEG_BINARY, "-y",
                "-i", temp_path,
                "-filter:a", f"atempo={atempo_value}",
                "-vn",  # Только аудио
                speed_temp_path
            ]

            try:
                print(f"[AUDIO] Changing speed to {atempo_value}x with ffmpeg...")
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True, timeout=30)
                final_audio_path = speed_temp_path
                # Удаляем оригинальный файл
                os.unlink(temp_path)
                print(f"[AUDIO] Speed changed successfully")
            except Exception as ffmpeg_error:
                print(f"[AUDIO] FFmpeg speed change failed: {ffmpeg_error}, using original speed")
                # Если не получилось - используем оригинал
                if os.path.exists(speed_temp_path):
                    os.unlink(speed_temp_path)
                final_audio_path = temp_path

        # Генерируем уникальное имя файла
        file_name = f"voiceover_{uuid.uuid4()}.mp3"

        # Загружаем в Supabase Storage
        with open(final_audio_path, "rb") as f:
            file_data = f.read()

        # Используем upsert для перезаписи файла если он уже существует
        res = supabase.storage.from_("videos").upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": "audio/mpeg", "upsert": "true"}
        )

        # Удаляем временный файл
        if os.path.exists(final_audio_path):
            os.unlink(final_audio_path)

        # Получаем публичный URL
        # Если bucket публичный - используем get_public_url
        # Если приватный - используем signed URL (действует 1 год)
        try:
            public_url = supabase.storage.from_("videos").get_public_url(file_name)
            return public_url
        except Exception:
            # Fallback: создаем signed URL на 1 год
            signed_url = supabase.storage.from_("videos").create_signed_url(
                file_name,
                expires_in=31536000  # 1 год в секундах
            )
            return signed_url['signedURL']

    except Exception as e:
        # Очищаем временные файлы в случае ошибки
        for path_var in ['temp_path', 'final_audio_path', 'speed_temp_path']:
            if path_var in locals():
                path = locals()[path_var]
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass
        raise Exception(f"Failed to generate voiceover: {str(e)}")


def generate_subtitles_from_audio(audio_path: str) -> str:
    """
    Генерирует точные субтитры из аудио файла используя Whisper
    Это даёт идеальную синхронизацию с озвучкой

    Args:
        audio_path: Путь к аудио файлу

    Returns:
        str: Содержимое SRT файла
    """
    try:
        print(f"[WHISPER] Generating subtitles from audio: {audio_path}")

        # Используем whisper через командную строку
        # whisper audio.mp3 --model tiny --language ru --output_format srt --output_dir /tmp
        output_dir = tempfile.gettempdir()

        cmd = [
            "whisper",
            audio_path,
            "--model", "base",  # base - лучший баланс скорости/точности
            "--language", "ru",
            "--output_format", "srt",
            "--output_dir", output_dir,
            "--word_timestamps", "True",  # Точная синхронизация по словам
            "--prepend_punctuations", "\"¿([{-",
            "--append_punctuations", "\".,!?:)]}"
        ]

        print(f"[WHISPER] Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            # Whisper создаёт файл с именем исходного файла + .srt
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            srt_path = os.path.join(output_dir, f"{base_name}.srt")

            if os.path.exists(srt_path):
                with open(srt_path, 'r', encoding='utf-8') as f:
                    srt_content = f.read()

                # Удаляем временный файл
                os.unlink(srt_path)

                print(f"[WHISPER] Successfully generated {len(srt_content)} bytes of subtitles")
                return srt_content
            else:
                print(f"[WHISPER] SRT file not found: {srt_path}")
                return ""
        else:
            print(f"[WHISPER] Error: {result.stderr}")
            return ""

    except Exception as e:
        print(f"[WHISPER] Exception: {str(e)}")
        return ""


def generate_subtitles(text: str, duration: float, start_offset: float = 0.1) -> str:
    """
    Генерирует простые субтитры в формате SRT
    Разделяет текст на короткие фразы для лучшей читаемости
    Добавляет минимальное смещение для учёта задержки TTS

    Args:
        text: Текст для субтитров
        duration: Общая длительность видео в секундах
        start_offset: Начальное смещение в секундах (минимальное для лучшей синхронизации)

    Returns:
        str: Содержимое SRT файла
    """
    # Сначала разбиваем по предложениям
    sentences = text.replace("! ", "!|").replace("? ", "?|").replace(". ", ".|").split("|")
    sentences = [s.strip() for s in sentences if s.strip()]

    # Затем разбиваем длинные предложения на короткие фразы (по запятым и союзам)
    phrases = []
    for sentence in sentences:
        # Если предложение длинное (>50 символов), разбиваем его
        if len(sentence) > 50:
            # Разбиваем по запятым, союзам "и", "но", "а", многоточиям
            parts = sentence.replace(", ", ",|").replace("... ", "...|").replace(" и ", " и|").replace(" но ", " но|").replace(" а ", " а|").split("|")
            for part in parts:
                part = part.strip()
                if part and part != "...":  # Пропускаем чистые паузы
                    phrases.append(part)
        else:
            phrases.append(sentence)

    if not phrases:
        return ""

    # Вычитаем смещение и небольшой отступ в конце
    usable_duration = max(duration - start_offset - 0.2, 1.0)

    # Рассчитываем время для каждой фразы
    time_per_phrase = usable_duration / len(phrases)

    srt_content = ""
    for i, phrase in enumerate(phrases):
        # Добавляем смещение ко всем временам
        start_time = start_offset + (i * time_per_phrase)
        end_time = start_offset + ((i + 1) * time_per_phrase)

        # Форматируем время в формат SRT: HH:MM:SS,mmm
        start_str = format_srt_time(start_time)
        end_str = format_srt_time(end_time)

        srt_content += f"{i + 1}\n"
        srt_content += f"{start_str} --> {end_str}\n"
        srt_content += f"{phrase}\n\n"

    return srt_content


def format_srt_time(seconds: float) -> str:
    """Форматирует время в формат SRT: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


async def upload_subtitles(srt_content: str, project_id: str) -> str:
    """
    Загружает субтитры в Supabase Storage

    Args:
        srt_content: Содержимое SRT файла
        project_id: ID проекта

    Returns:
        str: Публичный URL загруженного файла субтитров
    """
    try:
        file_name = f"subtitles_{project_id}.srt"

        # Используем upsert для перезаписи файла если он уже существует
        res = supabase.storage.from_("videos").upload(
            path=file_name,
            file=srt_content.encode('utf-8'),
            file_options={"content-type": "text/plain", "upsert": "true"}
        )

        # Получаем публичный URL
        try:
            public_url = supabase.storage.from_("videos").get_public_url(file_name)
            return public_url
        except Exception:
            # Fallback: создаем signed URL на 1 год
            signed_url = supabase.storage.from_("videos").create_signed_url(
                file_name,
                expires_in=31536000  # 1 год в секундах
            )
            return signed_url['signedURL']

    except Exception as e:
        raise Exception(f"Failed to upload subtitles: {str(e)}")
