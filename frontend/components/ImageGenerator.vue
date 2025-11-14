<template>
  <div class="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-5 border border-slate-700/50 h-full flex flex-col transition-all duration-300 hover:border-yellow-400/40">
    <!-- Шапка -->
    <div class="flex justify-between items-center mb-4">
      <span class="text-sm font-bold text-slate-200">Сцена {{ scene.scene_number }}</span>
      <div class="flex gap-2">
        <select 
          v-model="selectedStyle" 
          class="select select-sm bg-slate-800/60 border border-slate-700/50 text-slate-200 rounded-lg focus:outline-none focus:border-yellow-400 pl-3 pr-8"
        >
          <option value="" class="bg-slate-800 text-slate-200">Стандартный</option>
          <option value="cinematic" class="bg-slate-800 text-slate-200">Кинематографичный</option>
          <option value="cartoon" class="bg-slate-800 text-slate-200">Мультфильм</option>
          <option value="pixel art" class="bg-slate-800 text-slate-200">Пиксель-арт</option>
          <option value="realistic" class="bg-slate-800 text-slate-200">Реалистичный</option>
          <option value="minimalist" class="bg-slate-800 text-slate-200">Минимализм</option>
        </select>
        <button 
          class="btn btn-sm w-10 h-10 p-0 rounded-full flex items-center justify-center bg-gradient-to-r from-yellow-400 to-blue-500 text-white border-0 shadow-sm hover:shadow-md transition-all group relative overflow-hidden"
          @click="regenerateWithStyle"
          :disabled="isGenerating"
          aria-label="Перегенерировать"
        >
          <!-- Мазок света при наведении -->
          <div class="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-full transition-transform duration-500"></div>
          <svg 
            v-if="!isGenerating" 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="2"
            class="relative z-10"
          >
            <path d="M2.5 2v6h6M3 12.24A9.5 9.5 0 0 0 21 12c0 1.77-.68 3.37-1.82 4.6" />
            <path d="M21.5 22v-6h-6M21 12.24A9.5 9.5 0 0 0 3 12c0-1.77.68-3.37 1.82-4.6" />
          </svg>
          <span 
            v-else 
            class="loading loading-spinner loading-xs text-white relative z-10"
          ></span>
        </button>
      </div>
    </div>

    <!-- Контейнер изображения -->
    <div class="flex-1 flex items-center justify-center bg-slate-900/30 rounded-xl overflow-hidden relative border-2 border-dashed border-slate-700/40">
      <!-- Загрузка / Генерация -->
      <div v-if="isGenerating || imageLoading" class="text-center p-6 w-full">
        <!-- Van Gogh-спиннер -->
        <div class="loading-spinner mb-4 mx-auto">
          <div class="loading-inner"></div>
        </div>
        <p class="text-slate-300 text-sm mb-2">{{ imageLoading ? 'Загружаю изображение...' : 'Генерирую изображение...' }}</p>
        <p class="text-xs text-slate-500 mt-1">{{ progressText }}</p>
        
        <!-- Анимированные "мазки" -->
        <div class="absolute inset-0 opacity-10 overflow-hidden pointer-events-none">
          <div class="absolute top-1/4 left-1/4 w-32 h-16 bg-yellow-400/30 rounded-full animate-pulse-slow"></div>
          <div class="absolute bottom-1/3 right-1/4 w-28 h-14 bg-blue-500/20 rounded-full animate-pulse-slower"></div>
        </div>
      </div>

      <!-- Ошибка -->
      <div v-else-if="error" class="text-center p-6">
        <div class="inline-block mb-3">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-red-400">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <p class="text-red-300 mb-3">{{ error }}</p>
        <button 
          class="btn btn-sm px-4 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40 rounded-lg transition-colors"
          @click="regenerateWithStyle"
        >
          Попробовать снова
        </button>
      </div>

      <!-- Нет изображения -->
      <div v-else-if="!scene.generated_image_url" class="text-center p-6">
        <div class="inline-block mb-3">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" class="text-yellow-400/40">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <path d="M21 15l-1.5-1.5" />
            <path d="M15.5 15.5l-1.5-1.5" />
            <path d="M10 15l-1.5-1.5" />
          </svg>
        </div>
        <p class="text-slate-500 text-sm">Изображение ещё не сгенерировано</p>
      </div>

      <!-- Изображение (как картина) -->
      <div v-else class="p-2 relative rounded-lg bg-gradient-to-br from-yellow-400/5 to-blue-500/5 border border-yellow-400/20">
        <img
          :src="scene.generated_image_url"
          :alt="`Сцена ${scene.scene_number}`"
          class="max-h-[300px] max-w-full object-contain rounded"
          @load="handleImageLoad"
          @error="handleImageError"
          :style="{ display: imageLoaded ? 'block' : 'none' }"
        />
        <!-- Тень-рамка -->
        <div class="absolute inset-0 rounded-lg shadow-[0_0_20px_rgba(253,224,71,0.1)] pointer-events-none"></div>
      </div>
    </div>

    <!-- Промпт -->
    <div v-if="scene.visual_prompt" class="mt-3 p-3 bg-slate-800/30 rounded-xl text-xs text-slate-400 max-h-20 overflow-y-auto border border-slate-700/40">
      <span class="text-slate-300 font-medium">Промпт:</span> {{ scene.visual_prompt }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  scene: {
    type: Object,
    required: true
  },
  isGenerating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['regenerate'])

const selectedStyle = ref('')
const progressText = ref('Обрабатываю запрос...')
const error = ref(null)
const imageLoading = ref(false)
const imageLoaded = ref(false)

// Отслеживаем изменение URL изображения
watch(() => props.scene.generated_image_url, (newUrl) => {
  if (newUrl) {
    imageLoading.value = true
    imageLoaded.value = false
  }
})

watch(() => props.isGenerating, (newVal) => {
  if (newVal) {
    error.value = null
    imageLoaded.value = false
    const progress = ['Анализ сцены...', 'Создание промпта...', 'Генерация изображения...', 'Обработка...']
    let i = 0
    const interval = setInterval(() => {
      progressText.value = progress[i % progress.length]
      i++
    }, 800)

    setTimeout(() => clearInterval(interval), 60000)
  }
})

const handleImageLoad = () => {
  imageLoading.value = false
  imageLoaded.value = true
}

const handleImageError = () => {
  imageLoading.value = false
  imageLoaded.value = false
  error.value = 'Не удалось загрузить изображение'
}

const regenerateWithStyle = () => {
  error.value = null
  imageLoaded.value = false
  emit('regenerate', {
    sceneId: props.scene.id,
    style: selectedStyle.value || null
  })
}
</script>

<template>
  <div class="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-5 border border-slate-700/50 h-full flex flex-col transition-all duration-300 hover:border-yellow-400/40">
    <!-- Шапка -->
    <div class="flex justify-between items-center mb-4">
      <span class="text-sm font-bold text-slate-200">Сцена {{ scene.scene_number }}</span>
      <div class="flex gap-2">
        <select 
          v-model="selectedStyle" 
          class="select select-sm bg-slate-800/60 border border-slate-700/50 text-slate-200 rounded-lg focus:outline-none focus:border-yellow-400 pl-3 pr-8"
        >
          <option value="" class="bg-slate-800 text-slate-200">Стандартный</option>
          <option value="cinematic" class="bg-slate-800 text-slate-200">Кинематографичный</option>
          <option value="cartoon" class="bg-slate-800 text-slate-200">Мультфильм</option>
          <option value="pixel art" class="bg-slate-800 text-slate-200">Пиксель-арт</option>
          <option value="realistic" class="bg-slate-800 text-slate-200">Реалистичный</option>
          <option value="minimalist" class="bg-slate-800 text-slate-200">Минимализм</option>
        </select>
        <button 
          class="btn btn-sm w-10 h-10 p-0 rounded-full flex items-center justify-center bg-gradient-to-r from-yellow-400 to-blue-500 text-white border-0 shadow-sm hover:shadow-md transition-all group relative overflow-hidden"
          @click="regenerateWithStyle"
          :disabled="isGenerating"
          aria-label="Перегенерировать"
        >
          <!-- Мазок света при наведении -->
          <div class="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-full transition-transform duration-500"></div>
          <svg 
            v-if="!isGenerating" 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="2"
            class="relative z-10"
          >
            <path d="M2.5 2v6h6M3 12.24A9.5 9.5 0 0 0 21 12c0 1.77-.68 3.37-1.82 4.6" />
            <path d="M21.5 22v-6h-6M21 12.24A9.5 9.5 0 0 0 3 12c0-1.77.68-3.37 1.82-4.6" />
          </svg>
          <span 
            v-else 
            class="loading loading-spinner loading-xs text-white relative z-10"
          ></span>
        </button>
      </div>
    </div>

    <!-- Контейнер изображения -->
    <div class="flex-1 flex items-center justify-center bg-slate-900/30 rounded-xl overflow-hidden relative border-2 border-dashed border-slate-700/40">
      <!-- Загрузка / Генерация -->
      <div v-if="isGenerating || imageLoading" class="text-center p-6 w-full">
        <!-- Van Gogh-спиннер -->
        <div class="loading-spinner mb-4 mx-auto">
          <div class="loading-inner"></div>
        </div>
        <p class="text-slate-300 text-sm mb-2">{{ imageLoading ? 'Загружаю изображение...' : 'Генерирую изображение...' }}</p>
        <p class="text-xs text-slate-500 mt-1">{{ progressText }}</p>
        
        <!-- Анимированные "мазки" -->
        <div class="absolute inset-0 opacity-10 overflow-hidden pointer-events-none">
          <div class="absolute top-1/4 left-1/4 w-32 h-16 bg-yellow-400/30 rounded-full animate-pulse-slow"></div>
          <div class="absolute bottom-1/3 right-1/4 w-28 h-14 bg-blue-500/20 rounded-full animate-pulse-slower"></div>
        </div>
      </div>

      <!-- Ошибка -->
      <div v-else-if="error" class="text-center p-6">
        <div class="inline-block mb-3">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-red-400">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <p class="text-red-300 mb-3">{{ error }}</p>
        <button 
          class="btn btn-sm px-4 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40 rounded-lg transition-colors"
          @click="regenerateWithStyle"
        >
          Попробовать снова
        </button>
      </div>

      <!-- Нет изображения -->
      <div v-else-if="!scene.generated_image_url" class="text-center p-6">
        <div class="inline-block mb-3">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" class="text-yellow-400/40">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <path d="M21 15l-1.5-1.5" />
            <path d="M15.5 15.5l-1.5-1.5" />
            <path d="M10 15l-1.5-1.5" />
          </svg>
        </div>
        <p class="text-slate-500 text-sm">Изображение ещё не сгенерировано</p>
      </div>

      <!-- Изображение (как картина) -->
      <div v-else class="p-2 relative rounded-lg bg-gradient-to-br from-yellow-400/5 to-blue-500/5 border border-yellow-400/20">
        <img
          :src="scene.generated_image_url"
          :alt="`Сцена ${scene.scene_number}`"
          class="max-h-[300px] max-w-full object-contain rounded"
          @load="handleImageLoad"
          @error="handleImageError"
          :style="{ display: imageLoaded ? 'block' : 'none' }"
        />
        <!-- Тень-рамка -->
        <div class="absolute inset-0 rounded-lg shadow-[0_0_20px_rgba(253,224,71,0.1)] pointer-events-none"></div>
      </div>
    </div>

    <!-- Промпт -->
    <div v-if="scene.visual_prompt" class="mt-3 p-3 bg-slate-800/30 rounded-xl text-xs text-slate-400 max-h-20 overflow-y-auto border border-slate-700/40">
      <span class="text-slate-300 font-medium">Промпт:</span> {{ scene.visual_prompt }}
    </div>
  </div>
</template>