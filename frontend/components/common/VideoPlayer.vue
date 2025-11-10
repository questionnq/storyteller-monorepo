<template>
  <div v-if="videoUrl" class="bg-base-200 rounded-lg p-4 shadow-lg">
    <h3 class="text-lg font-bold mb-3">{{ title }}</h3>
    <video controls class="w-full max-h-96">
      <source :src="videoUrl" type="video/mp4">
      Ваш браузер не поддерживает видео.
    </video>
    <div class="mt-4 flex gap-2">
      <button class="btn btn-primary btn-sm" @click="downloadVideo">
        Скачать .mp4
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  videoUrl: { type: String, default: null },
  title: { type: String, default: 'Готовое видео' }
})

const downloadVideo = () => {
  if (props.videoUrl) {
    const link = document.createElement('a')
    link.href = props.videoUrl
    link.download = 'storyboard-video.mp4'
    link.click()
  }
}
</script>