"""
Сервис для создания видео из изображений (слайд-шоу) с фоновым видео
"""
import os
import tempfile
import uuid
import requests
from typing import List, Dict
from moviepy.editor import (
    ImageClip, VideoFileClip, concatenate_videoclips,
    AudioFileClip, CompositeVideoClip, TextClip
)
from PIL import Image, ImageDraw, ImageFont
from app.db.supa_request import supabase


# Пути к фоновым видео
BACKGROUND_VIDEOS = {
    "minecraft": "backend/assets/backgrounds/minecraft.mp4",
    "subway": "backend/assets/backgrounds/subway.mp4",
    "abstract": "backend/assets/backgrounds/abstract.mp4",
}


async def create_slideshow_video(
    scenes: List[Dict],
    voiceover_url: str = None,
    subtitle_content: str = None,
    total_duration: float = 30.0,
    background_style: str = "minecraft"
) -> str:
    """
    Создает слайд-шоу видео из изображений сцен с фоновым видео

    Args:
        scenes: Список сцен с generated_image_url
        voiceover_url: URL аудио озвучки (опционально)
        subtitle_content: Содержимое субтитров в формате SRT (опционально)
        total_duration: Общая длительность видео в секундах
        background_style: Стиль фонового видео ('minecraft', 'subway', 'abstract')

    Returns:
        str: Публичный URL загруженного видео
    """
    temp_files = []
    clips = []

    try:
        # Фильтруем сцены с изображениями
        valid_scenes = [s for s in scenes if s.get("generated_image_url")]

        if not valid_scenes:
            raise ValueError("No scenes with generated images found")

        # Рассчитываем длительность для каждого изображения
        duration_per_scene = total_duration / len(valid_scenes)

        # Размеры для вертикального видео 9:16 (1080x1920)
        video_width = 1080
        video_height = 1920

        # Проверяем наличие фонового видео
        background_path = BACKGROUND_VIDEOS.get(background_style)
        background_clip = None

        if background_path and os.path.exists(background_path):
            # Загружаем фоновое видео
            background_clip = VideoFileClip(background_path)

            # Зацикливаем фоновое видео если оно короче нужной длительности
            if background_clip.duration < total_duration:
                num_loops = int(total_duration / background_clip.duration) + 1
                background_clip = background_clip.loop(n=num_loops)

            # Обрезаем до нужной длительности
            background_clip = background_clip.subclip(0, total_duration)
        else:
            # Если нет фонового видео - создаем черный фон
            black_bg_path = create_solid_color_image(video_width, video_height, (0, 0, 0))
            temp_files.append(black_bg_path)
            background_clip = ImageClip(black_bg_path, duration=total_duration)

        # Создаем клипы из каждого изображения
        for i, scene in enumerate(valid_scenes):
            image_url = scene.get("generated_image_url")

            # Скачиваем изображение
            img_response = requests.get(image_url)
            img_response.raise_for_status()

            # Сохраняем во временный файл
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_img.write(img_response.content)
            temp_img.close()
            temp_files.append(temp_img.name)

            # Обрабатываем изображение - делаем меньше для наложения на фон
            img = Image.open(temp_img.name)
            # Размещаем картинку в верхней части экрана (занимает 60% высоты)
            overlay_height = int(video_height * 0.6)
            overlay_width = int(overlay_height * img.width / img.height)

            img_resized = img.resize((overlay_width, overlay_height), Image.Resampling.LANCZOS)

            # Сохраняем обработанное изображение
            temp_processed = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img_resized.save(temp_processed.name, quality=95)
            temp_processed.close()
            temp_files.append(temp_processed.name)

            # Создаем видео клип из изображения
            start_time = i * duration_per_scene
            clip = (ImageClip(temp_processed.name)
                   .set_duration(duration_per_scene)
                   .set_start(start_time)
                   .set_position(("center", 50)))  # Центрируем по горизонтали, сверху
            clips.append(clip)

        # Накладываем все клипы на фоновое видео
        final_video = CompositeVideoClip([background_clip] + clips, size=(video_width, video_height))

        # Добавляем аудио озвучку, если есть
        if voiceover_url:
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            audio_response = requests.get(voiceover_url)
            audio_response.raise_for_status()
            audio_temp.write(audio_response.content)
            audio_temp.close()
            temp_files.append(audio_temp.name)

            audio_clip = AudioFileClip(audio_temp.name)

            # Подгоняем длительность видео под аудио (если аудио длиннее)
            if audio_clip.duration > final_video.duration:
                final_video = final_video.set_duration(audio_clip.duration)

            final_video = final_video.set_audio(audio_clip)

        # Добавляем субтитры, если есть
        if subtitle_content:
            final_video = add_subtitles_to_video(final_video, subtitle_content)

        # Экспортируем финальное видео
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_temp.close()
        temp_files.append(output_temp.name)

        final_video.write_videofile(
            output_temp.name,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4
        )

        # Загружаем в Supabase Storage
        file_name = f"video_{uuid.uuid4()}.mp4"

        with open(output_temp.name, "rb") as f:
            file_data = f.read()

        # Используем upsert для перезаписи файла если он уже существует
        res = supabase.storage.from_("videos").upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": "video/mp4", "upsert": "true"}
        )

        # Получаем публичный URL
        public_url = supabase.storage.from_("videos").get_public_url(file_name)

        return public_url

    except Exception as e:
        raise Exception(f"Failed to create video: {str(e)}")

    finally:
        # Очищаем все временные файлы
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass


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


def resize_and_crop(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Изменяет размер и обрезает изображение до целевого соотношения сторон

    Args:
        img: PIL Image объект
        target_width: Целевая ширина
        target_height: Целевая высота

    Returns:
        Image.Image: Обработанное изображение
    """
    target_ratio = target_width / target_height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Изображение шире целевого - обрезаем по ширине
        new_height = target_height
        new_width = int(new_height * img_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Обрезаем по центру
        left = (new_width - target_width) // 2
        img_cropped = img_resized.crop((left, 0, left + target_width, target_height))
    else:
        # Изображение выше целевого - обрезаем по высоте
        new_width = target_width
        new_height = int(new_width / img_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Обрезаем по центру
        top = (new_height - target_height) // 2
        img_cropped = img_resized.crop((0, top, target_width, top + target_height))

    return img_cropped


def add_subtitles_to_video(video_clip, srt_content: str):
    """
    Добавляет субтитры на видео (упрощенная версия)

    Args:
        video_clip: VideoClip объект
        srt_content: Содержимое SRT файла

    Returns:
        CompositeVideoClip с субтитрами
    """
    # Парсим SRT контент
    subtitles = parse_srt(srt_content)

    text_clips = []

    for subtitle in subtitles:
        text_clip = TextClip(
            subtitle["text"],
            fontsize=40,
            color="white",
            bg_color="black",
            size=(video_clip.w - 100, None),
            method="caption"
        ).set_position(("center", "bottom")).set_start(subtitle["start"]).set_duration(
            subtitle["end"] - subtitle["start"]
        )

        text_clips.append(text_clip)

    # Комбинируем видео с текстовыми клипами
    if text_clips:
        return CompositeVideoClip([video_clip] + text_clips)

    return video_clip


def parse_srt(srt_content: str) -> List[Dict]:
    """
    Парсит SRT контент в список субтитров

    Args:
        srt_content: Содержимое SRT файла

    Returns:
        List[Dict]: Список с временем и текстом субтитров
    """
    subtitles = []
    blocks = srt_content.strip().split("\n\n")

    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            # Парсим временные метки
            time_line = lines[1]
            start_str, end_str = time_line.split(" --> ")

            start_seconds = parse_srt_time(start_str)
            end_seconds = parse_srt_time(end_str)

            # Текст субтитра
            text = "\n".join(lines[2:])

            subtitles.append({
                "start": start_seconds,
                "end": end_seconds,
                "text": text
            })

    return subtitles


def parse_srt_time(time_str: str) -> float:
    """Парсит время из SRT формата в секунды"""
    time_str = time_str.strip()
    # Формат: HH:MM:SS,mmm
    hours, minutes, seconds = time_str.split(":")
    seconds, millis = seconds.split(",")

    total_seconds = (
        int(hours) * 3600 +
        int(minutes) * 60 +
        int(seconds) +
        int(millis) / 1000
    )

    return total_seconds
