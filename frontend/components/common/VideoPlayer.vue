<template>
  <div v-if="videoUrl" class="bg-base-200 rounded-lg p-4 shadow-lg">
    <h3 class="text-lg font-bold mb-3">{{ title }}</h3>

    <!-- DEBUG: Показываем URL -->
    <div class="mb-3 p-2 bg-base-300 rounded text-xs">
      <div class="font-semibold mb-1">🔍 Debug: Video URL</div>
      <div class="break-all opacity-70">{{ videoUrl }}</div>
    </div>

    <!-- Видео плеер -->
    <video
      controls
      class="w-full max-h-96 bg-black"
      @error="handleVideoError"
      @loadeddata="handleVideoLoaded"
    >
      <source :src="videoUrl" type="video/mp4">
      Ваш браузер не поддерживает видео.
    </video>

    <!-- Сообщение об ошибке -->
    <div v-if="videoError" class="alert alert-error mt-3">
      <span>❌ Ошибка загрузки видео: {{ videoError }}</span>
    </div>

    <!-- Кнопки действий -->
    <div class="mt-4 flex gap-2">
      <a
        :href="videoUrl"
        download="storyboard-video.mp4"
        target="_blank"
        class="btn btn-primary btn-sm"
      >
        📥 Скачать .mp4
      </a>
      <a
        :href="videoUrl"
        target="_blank"
        class="btn btn-outline btn-sm"
      >
        🔗 Открыть в новой вкладке
      </a>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  videoUrl: { type: String, default: null },
  title: { type: String, default: 'Готовое видео' }
})

const videoError = ref(null)

const handleVideoError = (event) => {
  console.error('[VideoPlayer] Video load error:', event)
  console.error('[VideoPlayer] Video URL:', props.videoUrl)
  console.error('[VideoPlayer] Error details:', event.target.error)

  if (event.target.error) {
    const errorCode = event.target.error.code
    const errorMessages = {
      1: 'MEDIA_ERR_ABORTED - Загрузка видео прервана пользователем',
      2: 'MEDIA_ERR_NETWORK - Ошибка сети при загрузке видео',
      3: 'MEDIA_ERR_DECODE - Ошибка декодирования видео (возможно поврежден файл)',
      4: 'MEDIA_ERR_SRC_NOT_SUPPORTED - Формат видео не поддерживается или URL недоступен'
    }
    videoError.value = errorMessages[errorCode] || `Неизвестная ошибка (код: ${errorCode})`
  } else {
    videoError.value = 'Не удалось загрузить видео'
  }
}

const handleVideoLoaded = () => {
  console.log('[VideoPlayer] Video loaded successfully!')
  videoError.value = null
}
</script>