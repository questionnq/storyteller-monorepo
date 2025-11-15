# 🎬 AI Video Generator

> **Автоматическая генерация видео из текстовых идей с использованием AI**

Превращайте текстовые идеи в полноценные видеоролики с озвучкой, субтитрами и стилизованными изображениями. Идеально для создания контента в стиле TikTok, YouTube Shorts и Instagram Reels.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/vue-3.5+-green.svg)](https://vuejs.org/)

---

## ✨ Возможности

- **🤖 AI-генерация сценариев** — создание профессиональных сценариев с помощью Google Gemini 2.5-Flash
- **🎨 Генерация изображений** — автоматическое создание стилизованных визуалов через FLUX, Pollinations и Stable Diffusion
- **🎙️ Озвучка** — преобразование текста в речь с помощью Google TTS с регулируемой скоростью
- **📝 Субтитры** — автоматическая генерация субтитров с синхронизацией через Whisper
- **🎥 Видео-рендеринг** — создание финальных видео в формате 9:16 (TikTok/Shorts)
- **🎮 Brainrot фоны** — выбор фоновых видео (Minecraft Parkour, Subway Surfers, абстрактные паттерны)
- **✏️ Редактирование** — полный контроль над сценарием и визуалами перед рендерингом
- **☁️ Облачное хранилище** — все медиафайлы хранятся в Supabase Storage

---

## 🎯 Как это работает

```
💡 Текстовая идея
    ↓
📝 AI генерирует сценарий (5 сцен)
    ↓
🎨 Генерация изображений для каждой сцены
    ↓
✏️ Редактирование (опционально)
    ↓
🎙️ Генерация озвучки + субтитров
    ↓
🎥 Сборка финального видео
    ↓
✅ Готовое видео для скачивания!
```

---

## 🛠 Технологический стек

### Backend
- **Python 3.11+** — основной язык программирования
- **FastAPI** — современный, быстрый веб-фреймворк
- **Supabase** — база данных (PostgreSQL) + хранилище файлов
- **FFmpeg** — обработка видео и аудио
- **Faster Whisper** — распознавание речи для субтитров

### Frontend
- **Nuxt 3** — мощный Vue фреймворк
- **Vue 3 Composition API** — современный подход к компонентам
- **Tailwind CSS** — utility-first CSS framework
- **DaisyUI** — красивые UI компоненты

### AI сервисы
- **Google Gemini 2.5-Flash** — генерация сценариев
- **FLUX Schnell** (Hugging Face) — генерация изображений
- **Pollinations AI** — fallback для изображений
- **Stable Diffusion** (Replicate) — дополнительная генерация
- **Google TTS** — синтез речи
- **Whisper** — распознавание речи

---

## 📦 Быстрый старт

### Предварительные требования

- Python 3.11+
- Node.js 18+
- FFmpeg (установлен в системе)
- Аккаунты:
  - [Supabase](https://supabase.com)
  - [Google AI Studio](https://ai.google.dev/)
  - [Hugging Face](https://huggingface.co/)
  - [Replicate](https://replicate.com/) (опционально)

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/ai-video-generator.git
cd ai-video-generator
```

### 2. Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp example.env .env
```

Отредактируйте `backend/.env`:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Google AI
GOOGLE_API_KEY=your-google-api-key

# Hugging Face
HF_TOKEN=your-huggingface-token

# Replicate (опционально)
REPLICATE_API_TOKEN=your-replicate-token

# Pollinations
POLLINATIONS_API_URL=https://image.pollinations.ai/prompt/
```

### 3. Настройка Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Создание .env файла
cp example.env .env
```

Отредактируйте `frontend/.env`:

```env
NUXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NUXT_PUBLIC_SUPABASE_KEY=your-anon-key
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4. Настройка базы данных

Выполните SQL-скрипты в Supabase SQL Editor:

```sql
-- Таблица проектов
CREATE TABLE public.projects (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  intro TEXT,
  tone TEXT,
  style TEXT,
  voiceover_url TEXT,
  subtitle_url TEXT,
  background_style TEXT DEFAULT 'minecraft',
  final_video_url TEXT,
  render_status TEXT DEFAULT 'pending',
  project_time REAL,
  user_id UUID REFERENCES auth.users(id),
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица сцен
CREATE TABLE public.scenes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  scene_number INTEGER NOT NULL,
  action TEXT,
  dialogue TEXT,
  voice_over TEXT,
  visual_prompt TEXT,
  generated_image_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Создание Storage buckets
INSERT INTO storage.buckets (id, name, public)
VALUES ('videos', 'videos', true);
```

### 5. Запуск приложения

**Backend (терминал 1):**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (терминал 2):**
```bash
cd frontend
npm run dev
```

Откройте http://localhost:3000 в браузере!

---

## 🏗 Архитектура проекта

```
ai-video-generator/
├── backend/                    # FastAPI приложение
│   ├── app/
│   │   ├── api/               # API роуты
│   │   │   └── v1/
│   │   │       └── routes.py  # Эндпоинты
│   │   ├── db/                # Работа с БД
│   │   │   └── supa_request.py
│   │   ├── service/           # Бизнес-логика
│   │   │   ├── gemini_script.py      # AI сценарии
│   │   │   ├── storyboard_service.py # Генерация изображений
│   │   │   ├── audio_service.py      # TTS + Whisper
│   │   │   └── video_service.py      # Рендеринг видео
│   │   └── core/
│   │       └── config.py      # Конфигурация
│   ├── assets/
│   │   └── backgrounds/       # Фоновые видео
│   ├── fonts/                 # Шрифты для субтитров
│   ├── main.py               # Точка входа
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                  # Nuxt 3 приложение
│   ├── pages/
│   │   ├── index.vue         # Главная страница
│   │   ├── dashboard.vue     # Список проектов
│   │   ├── login.vue         # Авторизация
│   │   └── project/
│   │       ├── [id].vue      # Редактор сценария
│   │       └── [id]/
│   │           └── render.vue # Видео-рендеринг
│   ├── components/
│   │   ├── common/           # Общие компоненты
│   │   │   ├── AudioPlayer.vue
│   │   │   ├── VideoPlayer.vue
│   │   │   └── RenderProgress.vue
│   │   ├── render/           # Компоненты рендера
│   │   │   ├── RenderSteps.vue
│   │   │   └── BackgroundSelector.vue
│   │   ├── SceneEditor.vue
│   │   └── ImageGenerator.vue
│   ├── composables/          # Переиспользуемая логика
│   │   ├── useApi.js
│   │   ├── usePolling.js
│   │   └── useSupabaseAuth.js
│   ├── nuxt.config.ts
│   └── package.json
│
├── CLAUDE.md                 # Контекст для Claude AI
└── README.md                 # Этот файл
```

---

## 🔄 Процесс создания видео

### 1. Генерация сценария
```http
POST /api/v1/generate-script
{
  "prompt": "Видео про котика на скейтборде",
  "tone": "юмористический",
  "style": "мультяшный",
  "project_time": 30
}
```

### 2. Генерация изображений
```http
POST /api/v1/generate-storyboard/{project_id}
```

### 3. Регенерация отдельной сцены
```http
POST /api/v1/regenerate-scene/{scene_id}
{
  "style_prompt": "в стиле киберпанк"
}
```

### 4. Генерация озвучки и субтитров
```http
POST /api/v1/generate-voiceover/{project_id}
```

### 5. Рендеринг видео
```http
POST /api/v1/render-video/{project_id}
{
  "background": "minecraft"
}
```

---

## 🎨 Кастомизация

### Добавление новых фонов

1. Поместите видео (9:16, .mp4) в `backend/assets/backgrounds/`
2. Добавьте в `frontend/pages/project/[id]/render.vue`:

```javascript
const backgrounds = [
  // ...existing backgrounds
  {
    value: 'your-bg',
    name: 'Ваш фон',
    description: 'Описание фона',
    emoji: '🎨'
  }
]
```

3. Обновите `backend/app/service/video_service.py`:

```python
BACKGROUND_VIDEOS = {
    # ...existing backgrounds
    "your-bg": os.path.join(_BACKEND_DIR, "assets", "backgrounds", "your-bg.mp4"),
}
```

### Настройка стилей субтитров

Редактируйте `backend/app/service/video_service.py`:

```python
# В функции convert_srt_to_ass()
Style: Default,FontName,FontSize,PrimaryColour,...
```

---

## 🚀 Деплой

### Heroku / Render (Backend)

```bash
# Dockerfile уже настроен
git push heroku main
```

### Vercel (Frontend)

```bash
vercel deploy
```

Убедитесь что установлены переменные окружения!

---

## 🐛 Известные проблемы

- **Кириллица в субтитрах**: Убедитесь что шрифт Impact поддерживает кириллицу (или используйте DejaVu Sans)
- **Memory limit**: При рендеринге больших видео может потребоваться >512MB RAM
- **FFmpeg**: Должен быть установлен в системе или Docker контейнере

---

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

## 🤝 Вклад в проект

Pull requests приветствуются! Для серьезных изменений сначала откройте Issue для обсуждения.

---

## 📧 Контакты

- GitHub: [@your-username](https://github.com/your-username)
- Email: your.email@example.com

---

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) за отличный фреймворк
- [Nuxt](https://nuxt.com/) за мощный Vue фреймворк
- [Supabase](https://supabase.com/) за BaaS платформу
- [Hugging Face](https://huggingface.co/) за доступ к AI моделям
- [Google](https://ai.google.dev/) за Gemini API

---
