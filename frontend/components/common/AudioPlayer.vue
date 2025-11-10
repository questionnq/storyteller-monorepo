<template>
  <div v-if="audioUrl" class="bg-base-200 rounded-lg p-4 shadow-lg">
    <h3 class="text-lg font-bold mb-3">{{ title }}</h3>
    <audio controls class="w-full">
      <source :src="audioUrl" type="audio/mpeg">
      Ваш браузер не поддерживает аудио.
    </audio>
  </div>
</template>

<script setup>
defineProps({
  audioUrl: { type: String, default: null },
  title: { type: String, default: 'Озвучка' }
})
</script>