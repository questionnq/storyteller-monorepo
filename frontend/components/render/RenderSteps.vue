<template>
  <div class="bg-base-200 rounded-lg p-4 shadow-lg">
    <h3 class="text-lg font-bold mb-4">Процесс сборки видео</h3>
    
    <ul class="steps steps-vertical w-full">
      <li 
        v-for="step in steps" 
        :key="step.id"
        class="step"
        :class="stepClass(step)"
      >
        <div class="step-content">
          <h4 class="font-semibold">{{ step.title }}</h4>
          <p class="text-sm opacity-70">{{ step.description }}</p>
        </div>
      </li>
    </ul>
    
    <div v-if="currentStatus === 'failed'" class="alert alert-error mt-4">
      <span>❌ Ошибка сборки. Попробуйте снова.</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  currentStatus: { type: String, default: 'pending' } // pending, voiceover, rendering, done, failed
})

const steps = [
  { id: 1, title: 'Озвучка', description: 'Генерация аудио и субтитров', status: 'voiceover' },
  { id: 2, title: 'Фон', description: 'Подготовка видео-фона', status: 'preparing' },
  { id: 3, title: 'Сборка', description: 'Синхронизация всех элементов', status: 'rendering' },
  { id: 4, title: 'Готово', description: 'Видео готово к скачиванию', status: 'done' }
]

const stepClass = (step) => {
  const status = props.currentStatus
  const stepIndex = steps.findIndex(s => s.status === status)
  const currentIndex = steps.findIndex(s => s.status === step.status)
  
  if (currentIndex < stepIndex) return 'step-primary'
  if (currentIndex === stepIndex) return 'step-accent step-active'
  return ''
}
</script>