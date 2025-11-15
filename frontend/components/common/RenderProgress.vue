<template>
  <div v-if="progress > 0" class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-5 border border-slate-700/50 fade-in-up" style="animation-delay: 0.1s">
    <h3 class="text-lg font-bold text-slate-100 mb-3 flex items-center gap-2">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M12 3v6m0 0l4-4m-4 4l-4-4" />
        <circle cx="12" cy="15" r="8" />
      </svg>
      Прогресс сборки
    </h3>
    <div class="h-3 bg-slate-700/50 rounded-full overflow-hidden relative">
      <div class="absolute inset-0 bg-gradient-to-r from-indigo-950/30 to-purple-950/30"></div>
      <div 
        class="h-full bg-gradient-to-r from-yellow-400 to-blue-500 rounded-full transition-all duration-500 ease-out" 
        :style="{ width: `${progress}%` }"
      >
        <div 
          v-if="progress > 0" 
          class="absolute right-0 top-1/2 w-2.5 h-2.5 -translate-y-1/2 bg-yellow-400 rounded-full animate-pulse"
          style="box-shadow: 0 0 6px rgba(253, 224, 71, 0.7);"
        ></div>
      </div>
    </div>
    <p class="text-slate-400 text-sm mt-2">{{ progressText }}</p>
  </div>
</template>

<script setup>
defineProps({
  progress: { type: Number, default: 0 },
  progressText: { type: String, default: '' }
})
</script>

<style scoped>
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