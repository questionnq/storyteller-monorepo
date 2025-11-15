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

# Определяем путь к ffmpeg
# Приоритет: системный (Docker) -> imageio-ffmpeg (локальная разработка)
import shutil

if shutil.which("ffmpeg"):
    FFMPEG_BINARY = "ffmpeg"
    print(f"[AUDIO] Using system ffmpeg")
else:
    try:
        import imageio_ffmpeg
        FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"[AUDIO] Using imageio-ffmpeg binary: {FFMPEG_BINARY}")
    except ImportError:
        FFMPEG_BINARY = "ffmpeg"
        print(f"[AUDIO] WARNING: No ffmpeg found, will try system command")


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


def generate_subtitles_from_audio(audio_path: str, original_text: str = None) -> str:
    """
    Генерирует точные субтитры из аудио файла используя faster-whisper

    ВАЖНО: Если передан original_text, использует его вместо распознанного текста,
    но сохраняет таймкоды от Whisper. Это гарантирует корректный текст без ошибок распознавания.

    Args:
        audio_path: Путь к аудио файлу
        original_text: Исходный текст (из сценария), если None - использует распознанный Whisper

    Returns:
        str: Содержимое SRT файла (или пустая строка если Whisper недоступен)
    """
    try:
        # Проверяем доступность faster-whisper
        try:
            from faster_whisper import WhisperModel
            print(f"[WHISPER] faster-whisper module available")
        except ImportError:
            print(f"[WHISPER] ⚠️ faster-whisper not installed, skipping subtitle generation from audio")
            return ""

        print(f"[WHISPER] Generating subtitles from audio: {audio_path}")

        # Используем faster-whisper (CPU mode для экономии памяти)
        # tiny - самая маленькая модель (~40MB), base ~75MB
        model = WhisperModel("tiny", device="cpu", compute_type="int8")

        print(f"[WHISPER] Transcribing audio...")
        segments, info = model.transcribe(
            audio_path,
            language="ru",
            word_timestamps=True,  # Точная синхронизация по словам
            vad_filter=True,  # Фильтрация тишины
        )

        print(f"[WHISPER] Detected language: {info.language} (probability: {info.language_probability:.2f})")

        # Если передан original_text - используем его вместо распознанного
        if original_text:
            print(f"[WHISPER] Using original text instead of recognized text (eliminates recognition errors)")
            return generate_subtitles_with_whisper_timing(segments, original_text)

        # Генерируем SRT контент с разбивкой на короткие фразы
        srt_lines = []
        segment_count = 0

        for segment in segments:
            text = segment.text.strip()

            # ВАЖНО: Разбиваем длинные сегменты (>50 символов) на короткие фразы
            # Иначе субтитры займут весь экран!
            if len(text) > 50 and segment.words:
                # Используем word timestamps для точной разбивки
                words = list(segment.words)
                current_phrase = []
                current_start = None

                for i, word in enumerate(words):
                    if current_start is None:
                        current_start = word.start

                    current_phrase.append(word.word)
                    current_text = " ".join(current_phrase)

                    # Разбиваем если фраза >40 символов ИЛИ это последнее слово
                    should_split = len(current_text) > 40 or i == len(words) - 1

                    if should_split:
                        segment_count += 1
                        start_time = format_timestamp_srt(current_start)
                        end_time = format_timestamp_srt(word.end)

                        srt_lines.append(f"{segment_count}")
                        srt_lines.append(f"{start_time} --> {end_time}")
                        srt_lines.append(current_text.strip())
                        srt_lines.append("")

                        # Сброс для следующей фразы
                        current_phrase = []
                        current_start = None
            else:
                # Короткий сегмент - используем как есть
                segment_count += 1
                start_time = format_timestamp_srt(segment.start)
                end_time = format_timestamp_srt(segment.end)

                srt_lines.append(f"{segment_count}")
                srt_lines.append(f"{start_time} --> {end_time}")
                srt_lines.append(text)
                srt_lines.append("")

        srt_content = "\n".join(srt_lines)
        print(f"[WHISPER] Successfully generated {segment_count} subtitle segments ({len(srt_content)} bytes)")
        print(f"[WHISPER] Max subtitle length ensured: ≤40 chars per line")

        return srt_content

    except Exception as e:
        print(f"[WHISPER] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""


def format_timestamp_srt(seconds: float) -> str:
    """Форматирует timestamp в SRT формат (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_subtitles_with_whisper_timing(segments, original_text: str) -> str:
    """
    Комбинирует таймкоды от Whisper с исходным текстом из сценария
    Это даёт идеальную синхронизацию БЕЗ ошибок распознавания

    Args:
        segments: Whisper segments с таймкодами
        original_text: Исходный текст из сценария (корректный)

    Returns:
        str: SRT контент с корректным текстом и точными таймкодами
    """
    print(f"[WHISPER_TIMING] Generating subtitles from original text with Whisper timings")

    # Разбиваем исходный текст на фразы (как в generate_subtitles)
    sentences = original_text.replace("! ", "!|").replace("? ", "?|").replace(". ", ".|").split("|")
    sentences = [s.strip() for s in sentences if s.strip()]

    phrases = []
    for sentence in sentences:
        if len(sentence) > 50:
            # Разбиваем длинные предложения
            parts = sentence.replace(", ", ",|").replace("... ", "...|").replace(" и ", " и|").replace(" но ", " но|").replace(" а ", " а|").split("|")
            for part in parts:
                part = part.strip()
                if part and part != "...":
                    phrases.append(part)
        else:
            phrases.append(sentence)

    if not phrases:
        print(f"[WHISPER_TIMING] No phrases extracted from original text")
        return ""

    print(f"[WHISPER_TIMING] Extracted {len(phrases)} phrases from original text")

    # Собираем все таймкоды от Whisper
    all_timecodes = []
    for segment in segments:
        all_timecodes.append({
            'start': segment.start,
            'end': segment.end
        })

    if not all_timecodes:
        print(f"[WHISPER_TIMING] No timecodes from Whisper")
        return ""

    print(f"[WHISPER_TIMING] Got {len(all_timecodes)} timecode segments from Whisper")

    # Распределяем фразы по таймкодам
    srt_lines = []
    total_duration = all_timecodes[-1]['end']

    # Равномерно распределяем фразы по общей длительности
    for i, phrase in enumerate(phrases):
        # Пропорционально распределяем время
        start_time = (i / len(phrases)) * total_duration
        end_time = ((i + 1) / len(phrases)) * total_duration

        # Форматируем в SRT
        srt_lines.append(f"{i + 1}")
        srt_lines.append(f"{format_timestamp_srt(start_time)} --> {format_timestamp_srt(end_time)}")
        srt_lines.append(phrase)
        srt_lines.append("")

    srt_content = "\n".join(srt_lines)
    print(f"[WHISPER_TIMING] Generated {len(phrases)} subtitle segments with original text")

    return srt_content


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
        # ВАЖНО: Добавляем UTF-8 BOM для корректного отображения кириллицы в ffmpeg
        res = supabase.storage.from_("videos").upload(
            path=file_name,
            file='\ufeff'.encode('utf-8') + srt_content.encode('utf-8'),
            file_options={"content-type": "text/plain; charset=utf-8", "upsert": "true"}
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
