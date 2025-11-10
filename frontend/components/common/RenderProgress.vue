<template>
  <div class="bg-base-200 rounded-lg p-4 shadow-lg" v-if="progress > 0">
    <h3 class="text-lg font-bold mb-2">Прогресс сборки</h3>
    <div class="w-full bg-base-300 rounded-full h-2">
      <div 
        class="bg-primary h-2 rounded-full transition-all duration-300"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
    <p class="text-sm opacity-70 mt-2">{{ progressText }}</p>
  </div>
</template>

<script setup>
defineProps({
  progress: { type: Number, default: 0 },
  progressText: { type: String, default: '' }
})
</script>