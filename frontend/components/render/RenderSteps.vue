<template>
  <div class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-5 border border-slate-700/50 fade-in-up" style="animation-delay: 0.1s">
    <h3 class="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M12 3v6m0 0l4-4m-4 4l-4-4" />
        <circle cx="12" cy="15" r="8" />
      </svg>
      Процесс сборки видео
    </h3>
    
    <ul class="space-y-4">
      <li 
        v-for="step in steps" 
        :key="step.id"
        class="relative pl-8 py-2"
        :class="stepClass(step)"
      >
        <!-- SVG-иконка шага -->
        <div class="absolute left-0 top-3 w-5 h-5 rounded-full flex items-center justify-center">
          <svg v-if="step.status === 'completed'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-green-400">
            <path d="M9 12l2 2 4-4" />
          </svg>
          <div v-else-if="step.status === currentStatus" class="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
          <div v-else class="w-2 h-2 bg-slate-500 rounded-full"></div>
        </div>
        <div>
          <h4 class="font-semibold text-slate-100">{{ step.title }}</h4>
          <p class="text-slate-400 text-sm">{{ step.description }}</p>
        </div>
      </li>
    </ul>
    
    <div v-if="currentStatus === 'failed'" class="mt-4 p-3 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
      <div class="flex items-center gap-2">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <span>Ошибка сборки. Попробуйте снова.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  currentStatus: { type: String, default: 'pending' }
})

const steps = [
  { id: 1, title: 'Изображения', description: 'Раскадровка сгенерирована', status: 'pending' },
  { id: 2, title: 'Озвучка', description: 'Генерация аудио и субтитров', status: 'audio_ready' },
  { id: 3, title: 'Сборка', description: 'Создание слайд-шоу', status: 'rendering' },
  { id: 4, title: 'Готово', description: 'Видео готово к скачиванию', status: 'completed' }
]

const stepClass = (step) => {
  const status = props.currentStatus
  const stepIndex = steps.findIndex(s => s.status === status)
  const currentIndex = steps.findIndex(s => s.status === step.status)

  return {
    'text-yellow-200': currentIndex <= stepIndex || status === 'completed',
    'text-slate-300': currentIndex > stepIndex && status !== 'completed'
  }
}
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