<template>
  <div>
    <main class="container mx-auto px-4 py-4 max-w-5xl">
      <!-- Заголовок -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-slate-100">
          Рендеринг: {{ project?.title }}
        </h1>
        <NuxtLink 
          :to="`/project/${route.params.id}`"
          class="btn btn-ghost px-4 py-2 text-slate-300 hover:text-slate-100 border border-slate-700/50 rounded-lg transition-colors"
        >
          ← Назад к сценарию
        </NuxtLink>
      </div>
      
      <!-- Табы навигации -->
      <div class="flex gap-2 mb-6">
        <NuxtLink 
          :to="`/project/${route.params.id}`"
          class="px-5 py-2.5 rounded-xl font-medium relative group transition-colors"
          :class="{
            'text-yellow-200': !$route.path.includes('/render'),
            'text-slate-400 hover:text-slate-200': $route.path.includes('/render')
          }"
        >
          <div class="flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <path d="M8 8h8" />
              <path d="M8 12h6" />
              <path d="M8 16h5" />
            </svg>
            Сценарий
          </div>
          <div 
            v-if="!$route.path.includes('/render')"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-yellow-400 rounded-full"
          ></div>
        </NuxtLink>
        <NuxtLink 
          :to="`/project/${route.params.id}/render`"
          class="px-5 py-2.5 rounded-xl font-medium relative group transition-colors"
          :class="{
            'text-yellow-200': $route.path.includes('/render'),
            'text-slate-400 hover:text-slate-200': !$route.path.includes('/render')
          }"
        >
          <div class="flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M21 21H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12l4 4v10a2 2 0 0 1-2 2z" />
              <path d="M10 10l4 4-4 4" />
            </svg>
            Рендер
          </div>
          <div 
            v-if="$route.path.includes('/render')"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-yellow-400 rounded-full"
          ></div>
        </NuxtLink>
      </div>
      
      <!-- Шаги процесса -->
      <RenderSteps :current-status="renderStatus" class="mb-6" />

      <!-- Предупреждение: нет изображений -->
      <div v-if="!hasGeneratedImages" class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-5 mb-6 border border-slate-700/50">
        <div class="flex gap-3">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-yellow-400 flex-shrink-0">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <div>
            <h3 class="font-bold text-slate-100 mb-1">Изображения не сгенерированы</h3>
            <p class="text-slate-300 text-sm mb-3">Для создания видео сначала сгенерируйте изображения на вкладке "Сценарий"</p>
            <NuxtLink
              :to="`/project/${route.params.id}`"
              class="btn btn-van-gogh-outline px-4 py-2 rounded-lg text-sm"
            >
              Перейти к сценарию
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Предпросмотр сценария -->
      <div v-if="project?.scenes && project.scenes.length > 0" class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-6 mb-6 border border-slate-700/50">
        <h2 class="text-xl font-bold text-slate-100 mb-4">📋 Предпросмотр сценария</h2>
        <div class="space-y-3 max-h-64 overflow-y-auto">
          <div
            v-for="scene in project.scenes"
            :key="scene.scene_number"
            class="p-3 bg-slate-800/30 rounded-lg text-sm border border-slate-700/40"
          >
            <div class="font-semibold text-slate-200 mb-1">Сцена {{ scene.scene_number }}</div>
            <div class="text-slate-400 text-xs">{{ scene.action }}</div>
            <div v-if="scene.dialogue" class="text-slate-300 text-xs mt-1 italic">💬 {{ scene.dialogue }}</div>
          </div>
        </div>
      </div>
      
      <!-- Шаг 1: Озвучка -->
      <div class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-6 mb-6 border border-slate-700/50">
        <h2 class="text-xl font-bold text-slate-100 mb-4">Шаг 1: Генерация озвучки</h2>

        <button
          v-if="!audioUrl && !isGeneratingAudio"
          class="btn btn-van-gogh-primary px-6 py-3 rounded-xl font-medium"
          @click="generateVoiceover"
          :disabled="!project?.scenes || project.scenes.length === 0"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="mr-2">
            <path d="M12 3v6m0 0l4-4m-4 4l-4-4" />
            <circle cx="12" cy="15" r="8" />
          </svg>
          Сгенерировать озвучку
        </button>

        <!-- Прогресс-бар в виде "мазка кисти" -->
        <div v-else-if="isGeneratingAudio" class="space-y-3">
          <div class="text-slate-200">Генерируется озвучка...</div>
          <div class="h-2.5 bg-slate-700/50 rounded-full overflow-hidden relative">
            <div class="absolute inset-0 bg-gradient-to-r from-yellow-400/20 to-blue-500/20"></div>
            <div class="h-full bg-gradient-to-r from-yellow-400 to-blue-500 rounded-full animate-pulse-slow" style="width: 0%; animation: brushStroke 4s infinite;"></div>
          </div>
          <p class="text-slate-400 text-sm">Это может занять до 30 секунд</p>
        </div>

        <AudioPlayer
          v-else-if="audioUrl"
          :audio-url="audioUrl"
          title="Готовая озвучка"
        />

        <!-- Субтитры -->
        <div v-if="subtitles" class="mt-4 p-4 bg-slate-800/30 rounded-xl border border-slate-700/40">
          <div class="flex items-center gap-2 mb-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-green-400">
              <path d="M9 12l2 2 4-4" />
            </svg>
            <h4 class="font-semibold text-slate-100">Субтитры сгенерированы</h4>
          </div>
          <p class="text-slate-400 text-xs">Субтитры будут автоматически добавлены в видео</p>
        </div>
      </div>
      
      <!-- Шаг 2: Выбор фона (с анимированными превью) -->
      <div class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-6 mb-6 border border-slate-700/50">
        <h2 class="text-xl font-bold text-slate-100 mb-4">Шаг 2: Выбор фонового видео</h2>
        <p class="text-slate-400 text-sm mb-4">Выберите brainrot фон для вашего видео</p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="bg in backgrounds"
            :key="bg.value"
            class="bg-slate-800/30 rounded-xl p-4 border-2 cursor-pointer transition-all hover:border-yellow-400/50 overflow-hidden"
            :class="{ 
              'border-yellow-400/80 bg-slate-800/50': renderSettings.background === bg.value,
              'opacity-50 cursor-not-allowed': status === 'processing' 
            }"
            @click="status !== 'processing' && (renderSettings.background = bg.value)"
          >
            <!-- Анимированное превью фона -->
            <div class="relative w-full h-24 mb-3 bg-slate-900/50 rounded-lg overflow-hidden">
              <div 
                v-if="bg.value === 'minecraft'" 
                class="absolute inset-0 animate-minecraft-bg"
              ></div>
              <div 
                v-else-if="bg.value === 'subway'" 
                class="absolute inset-0 animate-subway-bg"
              ></div>
              <div 
                v-else-if="bg.value === 'abstract'" 
                class="absolute inset-0 animate-abstract-bg"
              ></div>
            </div>
            <h4 class="font-semibold text-slate-200 text-sm mb-1">{{ bg.name }}</h4>
            <p class="text-slate-500 text-xs">{{ bg.description }}</p>
          </div>
        </div>

        <div class="mt-4 text-slate-400 text-sm">
          Текущий выбор: <span class="font-bold text-yellow-300">{{ getCurrentBackgroundName }}</span>
        </div>
      </div>

      <!-- Индикатор прогресса рендера -->
      <RenderProgress
        v-if="status === 'processing' && progress > 0"
        :progress="progress"
        :progress-text="progressText"
        class="mb-6"
      />

      <!-- Шаг 3: Сборка видео -->
      <div class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-6 mb-6 border border-slate-700/50">
        <h2 class="text-xl font-bold text-slate-100 mb-4">Шаг 3: Сборка видео</h2>

        <div v-if="!hasGeneratedImages" class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-4 mb-4 border border-slate-700/50">
          <div class="flex gap-3">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-yellow-400 flex-shrink-0">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span class="text-slate-300">Для создания видео нужны сгенерированные изображения</span>
          </div>
        </div>

        <button
          v-if="!videoUrl && status !== 'processing' && status !== 'done'"
          class="btn btn-van-gogh-primary px-6 py-3 rounded-xl font-medium"
          @click="startRender"
          :disabled="!hasGeneratedImages"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="mr-2">
            <path d="M21 21H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12l4 4v10a2 2 0 0 1-2 2z" />
            <path d="M10 10l4 4-4 4" />
          </svg>
          Собрать видео
        </button>

        <!-- Прогресс-бар в виде "живой картины" -->
        <div v-else-if="status === 'processing'" class="space-y-4">
          <div class="text-lg font-medium text-slate-100 flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M12 3v6m0 0l4-4m-4 4l-4-4" />
              <circle cx="12" cy="15" r="8" />
            </svg>
            Собираем ваше видео...
          </div>
          <div class="h-3 bg-slate-700/50 rounded-full overflow-hidden relative">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-950/30 to-purple-950/30"></div>
            <div 
              class="h-full bg-gradient-to-r from-yellow-400 to-blue-500 rounded-full" 
              :style="{ width: `${progress}%` }"
            >
              <!-- Анимированная "кисть" на конце прогресса -->
              <div 
                v-if="progress > 0" 
                class="absolute right-0 top-1/2 w-3 h-3 -translate-y-1/2 bg-yellow-400 rounded-full animate-pulse"
                style="box-shadow: 0 0 8px rgba(253, 224, 71, 0.8);"
              ></div>
            </div>
          </div>
          <p class="text-slate-400">{{ progressText }}</p>
          <p class="text-slate-500 text-sm">Это может занять до 2 минут</p>
        </div>

        <!-- Готовое видео -->
        <VideoPlayer
          v-else-if="videoUrl && videoUrl !== ''"
          :video-url="videoUrl"
          title="Готовое видео готово!"
        />

        <!-- Ошибка -->
        <div v-if="error" class="mt-4 p-4 bg-red-500/20 border border-red-500/40 rounded-xl text-red-300">
          <div class="flex items-center gap-2 mb-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span class="font-bold">Ошибка</span>
          </div>
          <p>{{ error }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '~/composables/useApi'
import { useSupabaseAuth } from '~/composables/useSupabaseAuth'
import RenderSteps from '~/components/RenderSteps.vue'
import RenderProgress from '~/components/RenderProgress.vue'
import AudioPlayer from '~/components/AudioPlayer.vue'
import VideoPlayer from '~/components/VideoPlayer.vue'

const route = useRoute()
const api = useApi()
const { generateVoiceover: apiGenerateVoiceover, startRender: apiStartRender, getRenderStatus } = api
const { user } = useSupabaseAuth()

// ... твой оригинальный скрипт без изменений ...

// Добавь вычисляемое свойство
const getCurrentBackgroundName = computed(() => {
  return backgrounds.find(bg => bg.value === renderSettings.value.background)?.name || 'Не выбран'
})
</script>

<style scoped>
/* Анимации для фона */

/* Minecraft: пиксельное мерцание */
@keyframes minecraftPulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
.animate-minecraft-bg {
  background: 
    linear-gradient(90deg, 
      rgba(253, 224, 71, 0.15) 25%, 
      transparent 25%,
      transparent 50%,
      rgba(253, 224, 71, 0.15) 50%,
      rgba(253, 224, 71, 0.15) 75%,
      transparent 75%
    ),
    linear-gradient(rgba(253, 224, 71, 0.05) 25%, transparent 25%);
  background-size: 20px 20px;
  animation: minecraftPulse 2s infinite;
}

/* Subway: движение вправо */
@keyframes subwayMove {
  0% { background-position: 0 0; }
  100% { background-position: 40px 0; }
}
.animate-subway-bg {
  background: 
    linear-gradient(90deg, 
      transparent 40%, 
      rgba(196, 181, 253, 0.15) 45%, 
      rgba(196, 181, 253, 0.15) 55%, 
      transparent 60%
    );
  background-size: 40px 100%;
  animation: subwayMove 1.5s linear infinite;
}

/* Abstract: плавные волны */
@keyframes abstractFloat {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(2px, -2px); }
  50% { transform: translate(-2px, 2px); }
  75% { transform: translate(2px, 2px); }
}
.animate-abstract-bg {
  background: 
    radial-gradient(circle at 20% 30%, rgba(103, 232, 249, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(103, 232, 249, 0.08) 0%, transparent 60%),
    radial-gradient(circle at 50% 20%, rgba(103, 232, 249, 0.07) 0%, transparent 55%);
  animation: abstractFloat 4s ease-in-out infinite;
}

/* Прогресс-бар */
@keyframes brushStroke {
  0% { width: 0%; opacity: 0.6; }
  50% { width: 70%; opacity: 1; }
  100% { width: 100%; opacity: 0.6; }
}
.animate-pulse-slow {
  animation: brushStroke 4s infinite;
}
</style>