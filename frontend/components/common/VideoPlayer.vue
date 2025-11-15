<template>
  <div v-if="videoUrl" class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-5 border border-slate-700/50 fade-in-up" style="animation-delay: 0.1s">
    <h3 class="text-lg font-bold text-slate-100 mb-3 flex items-center gap-2">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M21 21H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12l4 4v10a2 2 0 0 1-2 2z" />
        <path d="M10 10l4 4-4 4" />
      </svg>
      {{ title }}
    </h3>

    <!-- Видео плеер -->
    <video
      controls
      class="w-full max-h-96 rounded-xl bg-slate-900/50 border border-slate-700/40 shadow-lg hover:shadow-xl transition-shadow"
      @error="handleVideoError"
      @loadeddata="handleVideoLoaded"
    >
      <source :src="videoUrl" type="video/mp4">
      Ваш браузер не поддерживает видео.
    </video>

    <!-- Сообщение об ошибке -->
    <div v-if="videoError" class="mt-3 p-3 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
      <div class="flex items-center gap-2">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <span>{{ videoError }}</span>
      </div>
    </div>

    <!-- Кнопки действий -->
    <div class="mt-4 flex gap-2 flex-wrap">
      <a
        :href="videoUrl"
        download="storyboard-video.mp4"
        target="_blank"
        class="btn btn-van-gogh-primary px-4 py-2 rounded-lg text-sm"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        Скачать .mp4
      </a>
      <a
        :href="videoUrl"
        target="_blank"
        class="btn btn-van-gogh-outline px-4 py-2 rounded-lg text-sm"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1">
          <path d="M10 6h11v11" />
          <path d="M19 6l-9 9" />
        </svg>
        Открыть
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
  if (event.target.error) {
    const errorCode = event.target.error.code
    const errorMessages = {
      1: 'Загрузка прервана',
      2: 'Ошибка сети',
      3: 'Ошибка декодирования',
      4: 'Формат не поддерживается'
    }
    videoError.value = errorMessages[errorCode] || `Ошибка ${errorCode}`
  } else {
    videoError.value = 'Не удалось загрузить видео'
  }
}

const handleVideoLoaded = () => {
  videoError.value = null
}
</script>

<style scoped>
video::-webkit-media-controls-panel {
  background: linear-gradient(to bottom, rgba(15, 11, 31, 0.8), rgba(15, 11, 31, 0.9)) !important;
}
video::-webkit-media-controls-time-remaining-display,
video::-webkit-media-controls-current-time-display {
  color: #fde047 !important;
}
.fade-in-up {
  animation: fade-in-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(10px);
}
@keyframes fade-in-up {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>