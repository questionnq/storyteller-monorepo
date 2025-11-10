<template>
  <div>
    <AppHeader />
    
    <main class="container mx-auto px-4 py-4 max-w-5xl">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">
          Рендеринг: {{ project?.title }}
        </h1>
        <NuxtLink 
          :to="`/project/${route.params.id}`"
          class="btn btn-outline"
        >
          ← Назад к сценарию
        </NuxtLink>
      </div>
      
      <!-- Табы навигации -->
      <div class="tabs tabs-boxed mb-6">
        <NuxtLink 
          :to="`/project/${route.params.id}`"
          class="tab"
          :class="{ 'tab-active': $route.path.includes('/project/') && !$route.path.includes('/render') }"
        >
          📋 Сценарий
        </NuxtLink>
        <NuxtLink 
          :to="`/project/${route.params.id}/render`"
          class="tab"
          :class="{ 'tab-active': $route.path.includes('/render') }"
        >
          🎬 Рендер
        </NuxtLink>
      </div>
      
      <!-- Шаги процесса -->
      <RenderSteps :current-status="renderStatus" class="mb-6" />
      
      <!-- Предпросмотр сценария -->
      <div class="bg-base-200 rounded-lg p-6 shadow-lg mb-6" v-if="project?.script">
        <h2 class="text-xl font-bold mb-4">📋 Предпросмотр сценария</h2>
        <div class="space-y-3 max-h-64 overflow-y-auto">
          <div 
            v-for="scene in project.script.scenes" 
            :key="scene.scene_number"
            class="p-3 bg-base-300 rounded text-sm"
          >
            <div class="font-semibold mb-1">Сцена {{ scene.scene_number }}</div>
            <div class="text-xs opacity-70">{{ scene.action }}</div>
            <div v-if="scene.dialogue" class="text-xs mt-1 italic">💬 {{ scene.dialogue }}</div>
          </div>
        </div>
      </div>
      
      <!-- Шаг 1: Озвучка -->
      <div class="bg-base-200 rounded-lg p-6 shadow-lg mb-6">
        <h2 class="text-xl font-bold mb-4">Шаг 1: Генерация озвучки</h2>
        
        <button 
          v-if="!audioUrl && !isGeneratingAudio"
          class="btn btn-primary"
          @click="generateVoiceover"
          :disabled="!project.script"
        >
          🎙️ Сгенерировать озвучку
        </button>
        
        <AppLoader 
          v-else-if="isGeneratingAudio"
          title="Генерируется озвучка..."
          subtitle="Это может занять до 30 секунд"
        />
        
        <AudioPlayer 
          v-else-if="audioUrl"
          :audio-url="audioUrl"
          title="Готовая озвучка"
        />
        
        <!-- Субтитры -->
        <div v-if="subtitles" class="mt-4 p-4 bg-base-300 rounded">
          <h4 class="font-semibold mb-2">Сгенерированные субтитры:</h4>
          <pre class="text-xs whitespace-pre-wrap">{{ subtitles }}</pre>
        </div>
      </div>
      
      <!-- Шаг 2: Выбор фона -->
      <div class="bg-base-200 rounded-lg p-6 shadow-lg mb-6">
        <h2 class="text-xl font-bold mb-4">Шаг 2: Выбор фона</h2>
        <BackgroundSelector 
          v-model="renderSettings.background"
          :disabled="status === 'processing'"
          class="mb-4"
        />
        <div v-if="renderSettings.background === 'minecraft'" class="alert alert-info mt-4">
          <span>🎮 Minecraft фон идеален для игрового контента</span>
        </div>
      </div>
      
      <!-- Индикатор прогресса рендера -->
      <RenderProgress 
        v-if="progress > 0"
        :progress="progress"
        :progress-text="progressText"
        class="mb-6"
      />
      
      <!-- Шаг 3: Сборка видео -->
      <div class="bg-base-200 rounded-lg p-6 shadow-lg mb-6">
        <h2 class="text-xl font-bold mb-4">Шаг 3: Сборка видео</h2>
        
        <button 
          v-if="!videoUrl && status !== 'processing'"
          class="btn btn-primary btn-lg"
          @click="startRender"
          :disabled="!audioUrl || status === 'pending'"
        >
          🎬 Собрать видео
        </button>
        
        <AppLoader 
          v-else-if="status === 'processing'"
          title="Собираем ваше видео..."
          subtitle="Это может занять до 2 минут"
        />
        
        <VideoPlayer 
          v-else-if="videoUrl"
          :video-url="videoUrl"
          title="Готовое видео готово!"
        />
        
        <div v-if="error" class="alert alert-error mt-4">
          <span>❌ {{ error }}</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const route = useRoute()
const { generateVoiceover: apiGenerateVoiceover, startRender: apiStartRender, getRenderStatus } = useApi()
const { user } = useSupabaseAuth()

const project = ref(null)
const audioUrl = ref(null)
const subtitles = ref(null)
const isGeneratingAudio = ref(false)
const videoUrl = ref(null)
const status = ref('pending') // pending, voiceover, processing, done, failed
const error = ref(null)
const progress = ref(0)
const progressText = ref('')

const renderSettings = ref({
  background: 'minecraft'
})

// Проверка кэша при монтировании
onMounted(async () => {
  const projectId = route.params.id
  
  // Загружаем проект
  project.value = await $fetch(`/api/v1/projects/${projectId}`)
  
  // Проверяем кэш
  checkCachedFiles()
  
  // Горячие клавиши
  document.addEventListener('keydown', handleKeyboardShortcuts)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyboardShortcuts)
})

const checkCachedFiles = async () => {
  try {
    const projectId = route.params.id
    const cached = localStorage.getItem(`render_cache_${projectId}`)
    
    if (cached) {
      const cache = JSON.parse(cache)
      
      if (cache.audioUrl && cache.subtitles) {
        audioUrl.value = cache.audioUrl
        subtitles.value = cache.subtitles
        status.value = 'voiceover'
      }
      
      if (cache.videoUrl) {
        videoUrl.value = cache.videoUrl
        status.value = 'done'
      }
    }
  } catch (error) {
    console.error('Ошибка при проверке кэша:', error)
  }
}

const updateCache = () => {
  const projectId = route.params.id
  const cache = {
    audioUrl: audioUrl.value,
    subtitles: subtitles.value,
    videoUrl: videoUrl.value,
    timestamp: Date.now()
  }
  localStorage.setItem(`render_cache_${projectId}`, JSON.stringify(cache))
}

const handleError = (error, context) => {
  console.error(`Ошибка в ${context}:`, error)
  
  // Разные сообщения для разных типов ошибок
  if (error.message?.includes('network')) {
    error.value = 'Ошибка сети. Проверьте подключение к интернету.'
  } else if (error.message?.includes('timeout')) {
    error.value = 'Превышено время ожидания. Попробуйте снова.'
  } else {
    error.value = error.message || 'Произошла неизвестная ошибка'
  }
}

const handleKeyboardShortcuts = (event) => {
  // Ctrl/Cmd + Enter для запуска рендера
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    if (status.value === 'voiceover' && !videoUrl.value) {
      startRender()
    }
  }
  
  // Escape для отмены рендера
  if (event.key === 'Escape' && status.value === 'processing') {
    // Логика отмены рендера (заглушка)
    console.log('Отмена рендеринга...')
  }
}

const generateVoiceover = async () => {
  if (!project.value.script) return
  
  isGeneratingAudio.value = true
  
  try {
    const result = await apiGenerateVoiceover(route.params.id, project.value.script.scenes)
    audioUrl.value = result.audio_url
    subtitles.value = result.subtitles
    status.value = 'voiceover'
    updateCache()
  } catch (err) {
    handleError(err, 'generateVoiceover')
  } finally {
    isGeneratingAudio.value = false
  }
}

const startRender = async () => {
  status.value = 'processing'
  error.value = null
  progress.value = 0
  progressText.value = 'Подготовка...'
  
  try {
    await apiStartRender(route.params.id, renderSettings.value)
    pollStatus(route.params.id)
  } catch (err) {
    handleError(err, 'startRender')
    status.value = 'failed'
  }
}

const pollStatus = async (projectId) => {
  const { start, stop } = usePolling(async () => {
    try {
      const result = await getRenderStatus(projectId)
      status.value = result.status
      progress.value = result.progress || 0
      progressText.value = result.progress_text || ''
      
      if (result.status === 'done') {
        videoUrl.value = result.final_video_url
        updateCache()
        stop()
      } else if (result.status === 'failed') {
        error.value = result.error
        stop()
      }
    } catch (error) {
      handleError(error, 'pollStatus')
      stop()
    }
  }, 3000)
  
  start()
}
</script>