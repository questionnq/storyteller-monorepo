"""
Сервис для генерации озвучки (TTS) и субтитров
"""
import os
import tempfile
import uuid
from gtts import gTTS
from app.db.supa_request import supabase


async def generate_voiceover(text: str, lang: str = "ru") -> str:
    """
    Генерирует озвучку из текста с помощью Google TTS

    Args:
        text: Текст для озвучки
        lang: Язык озвучки (по умолчанию 'ru')

    Returns:
        str: Публичный URL загруженного аудио файла
    """
    try:
        # Генерируем аудио с помощью gTTS
        tts = gTTS(text=text, lang=lang, slow=False)

        # Создаем временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        # Сохраняем аудио во временный файл
        tts.save(temp_path)

        # Генерируем уникальное имя файла
        file_name = f"voiceover_{uuid.uuid4()}.mp3"

        # Загружаем в Supabase Storage
        with open(temp_path, "rb") as f:
            file_data = f.read()

        # Используем upsert для перезаписи файла если он уже существует
        res = supabase.storage.from_("videos").upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": "audio/mpeg", "upsert": "true"}
        )

        # Удаляем временный файл
        os.unlink(temp_path)

        # Получаем публичный URL
        public_url = supabase.storage.from_("videos").get_public_url(file_name)

        return public_url

    except Exception as e:
        # Очищаем временный файл в случае ошибки
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise Exception(f"Failed to generate voiceover: {str(e)}")


def generate_subtitles(text: str, duration: float) -> str:
    """
    Генерирует простые субтитры в формате SRT

    Args:
        text: Текст для субтитров
        duration: Общая длительность видео в секундах

    Returns:
        str: Содержимое SRT файла
    """
    # Простая генерация: разбиваем текст по предложениям
    sentences = text.replace("! ", "!|").replace("? ", "?|").replace(". ", ".|").split("|")
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return ""

    # Рассчитываем время для каждого предложения
    time_per_sentence = duration / len(sentences)

    srt_content = ""
    for i, sentence in enumerate(sentences):
        start_time = i * time_per_sentence
        end_time = (i + 1) * time_per_sentence

        # Форматируем время в формат SRT: HH:MM:SS,mmm
        start_str = format_srt_time(start_time)
        end_str = format_srt_time(end_time)

        srt_content += f"{i + 1}\n"
        srt_content += f"{start_str} --> {end_str}\n"
        srt_content += f"{sentence}\n\n"

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

        public_url = supabase.storage.from_("videos").get_public_url(file_name)
        return public_url

    except Exception as e:
        raise Exception(f"Failed to upload subtitles: {str(e)}")
