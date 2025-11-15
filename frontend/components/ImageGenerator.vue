<template>
  <div class="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-5 border border-slate-700/50 h-full flex flex-col transition-all duration-300 hover:border-yellow-400/40">

    <div class="flex justify-between items-center mb-4">
      <span class="text-sm font-bold text-slate-200">Сцена {{ scene.scene_number }}</span>
      <div class="flex gap-2">
        <div class="relative" ref="styleSelect">
          <button 
            @click="toggleStyleMenu"
            class="flex items-center gap-2 px-3 py-1.5 bg-slate-800/60 border border-slate-700/50 text-slate-200 rounded-lg focus:outline-none focus:border-yellow-400 transition-colors w-full justify-between"
          >
            <span>{{ selectedStyleLabel }}</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-slate-400">
              <polyline points="6,9 12,15 18,9" />
            </svg>
          </button>

          <div 
            v-show="isStyleMenuOpen"
            class="absolute z-10 mt-1 w-full bg-slate-800/90 backdrop-blur-sm rounded-lg border border-slate-700/50 shadow-lg overflow-hidden"
          >
            <button
              v-for="option in styleOptions"
              :key="option.value"
              @click="selectStyle(option.value)"
              class="w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-yellow-400/10 hover:text-yellow-200 transition-colors flex items-center gap-2"
            >
              <svg v-if="option.value === selectedStyle" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-yellow-400">
                <path d="M9 12l2 2 4-4" />
              </svg>
              <span>{{ option.label }}</span>
            </button>
          </div>
        </div>
        <button 
          class="btn btn-sm w-10 h-10 p-0 rounded-full flex items-center justify-center bg-gradient-to-r from-yellow-400 to-blue-500 text-white border-0 shadow-sm hover:shadow-md transition-all group relative overflow-hidden"
          @click="regenerateWithStyle"
          :disabled="isGenerating"
          aria-label="Перегенерировать"
        >
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
    <div class="flex-1 flex items-center justify-center bg-slate-900/30 rounded-xl overflow-hidden relative border-2 border-dashed border-slate-700/40">
      <div v-if="isGenerating || imageLoading" class="text-center p-6 w-full">
        <div class="loading-spinner mb-4 mx-auto">
          <div class="loading-inner"></div>
        </div>
        <p class="text-slate-300 text-sm mb-2">{{ imageLoading ? 'Загружаю изображение...' : 'Генерирую изображение...' }}</p>
        <p class="text-xs text-slate-500 mt-1">{{ progressText }}</p>
        <div class="absolute inset-0 opacity-10 overflow-hidden pointer-events-none">
          <div class="absolute top-1/4 left-1/4 w-32 h-16 bg-yellow-400/30 rounded-full animate-pulse-slow"></div>
          <div class="absolute bottom-1/3 right-1/4 w-28 h-14 bg-blue-500/20 rounded-full animate-pulse-slower"></div>
        </div>
      </div>
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
      <div v-else class="p-2 relative rounded-lg bg-gradient-to-br from-yellow-400/5 to-blue-500/5 border border-yellow-400/20">
        <img
          :src="scene.generated_image_url"
          :alt="`Сцена ${scene.scene_number}`"
          class="max-h-[300px] max-w-full object-contain rounded"
          @load="handleImageLoad"
          @error="handleImageError"
          :style="{ display: imageLoaded ? 'block' : 'none' }"
        />
        <div class="absolute inset-0 rounded-lg shadow-[0_0_20px_rgba(253,224,71,0.1)] pointer-events-none"></div>
      </div>
    </div>
    <div v-if="scene.visual_prompt" class="mt-3 p-3 bg-slate-800/30 rounded-xl text-xs text-slate-400 max-h-20 overflow-y-auto border border-slate-700/40">
      <span class="text-slate-300 font-medium">Промпт:</span> {{ scene.visual_prompt }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

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
const isStyleMenuOpen = ref(false)
const styleOptions = [
  { value: '', label: 'Стандартный' },
  { value: 'cinematic', label: 'Кинематографичный' },
  { value: 'cartoon', label: 'Мультфильм' },
  { value: 'pixel art', label: 'Пиксель-арт' },
  { value: 'realistic', label: 'Реалистичный' },
  { value: 'minimalist', label: 'Минимализм' }
]

const progressText = ref('Обрабатываю запрос...')
const error = ref(null)
const imageLoading = ref(false)
const imageLoaded = ref(false)

watch(() => props.scene.generated_image_url, (newUrl, oldUrl) => {
  console.log(`[ImageGenerator Scene ${props.scene.scene_number}] URL changed:`, { oldUrl, newUrl })

  if (newUrl && newUrl !== oldUrl) {
    console.log(`[ImageGenerator Scene ${props.scene.scene_number}] Setting imageLoading=true`)
    imageLoading.value = true
    imageLoaded.value = false
  }
  if (newUrl && !newUrl.includes('placehold.co') && !props.isGenerating) {
    console.log(`[ImageGenerator Scene ${props.scene.scene_number}] Image ready, setting imageLoading=false`)
    imageLoading.value = false
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

const selectedStyleLabel = computed(() => {
  return styleOptions.find(opt => opt.value === selectedStyle.value)?.label || 'Стандартный'
})

const styleSelect = ref(null)

const handleClickOutside = (event) => {
  if (styleSelect.value && !styleSelect.value.contains(event.target)) {
    isStyleMenuOpen.value = false
  }
}

const toggleStyleMenu = () => {
  isStyleMenuOpen.value = !isStyleMenuOpen.value
  if (isStyleMenuOpen.value) {
    setTimeout(() => {
      window.addEventListener('click', handleClickOutside)
    }, 0)
  } else {
    window.removeEventListener('click', handleClickOutside)
  }
}

const selectStyle = (value) => {
  selectedStyle.value = value
  isStyleMenuOpen.value = false
  window.removeEventListener('click', handleClickOutside)
}

onMounted(() => {
  if (props.scene?.visual_prompt?.includes('cinematic')) selectedStyle.value = 'cinematic'
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})

</script>

<style scoped>
.loading-spinner {
  width: 36px;
  height: 36px;
  position: relative;
}
.loading-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
  background: conic-gradient(
    transparent,
    #fde047 25%,
    #a78bfa 60%,
    transparent 85%
  );
  -webkit-mask: radial-gradient(farthest-side, transparent 85%, #000 85%);
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.02); }
}
@keyframes pulse-slower {
  0%, 100% { opacity: 0.15; transform: scale(1); }
  50% { opacity: 0.3; transform: scale(1.015); }
}
.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}
.animate-pulse-slower {
  animation: pulse-slower 6s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>