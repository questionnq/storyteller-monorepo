<template>
  <div v-if="audioUrl" class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-5 border border-slate-700/50 fade-in-up" style="animation-delay: 0.1s">
    <h3 class="text-lg font-bold text-slate-100 mb-3 flex items-center gap-2">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M12 3v6m0 0l4-4m-4 4l-4-4" />
        <circle cx="12" cy="15" r="8" />
      </svg>
      {{ title }}
    </h3>
    <audio 
      controls 
      class="w-full mt-2"
      :class="audioStyle"
    >
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

const audioStyle = 'appearance-none bg-slate-800/50 border border-slate-700/50 rounded-lg p-2'
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