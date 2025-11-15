<template>
  <div 
    v-if="notification.show" 
    class="fixed top-4 right-4 z-50 animate-fade-in"
    @mouseenter="pauseAutoClose"
    @mouseleave="resumeAutoClose"
  >
    <div 
      class="rounded-xl p-4 backdrop-blur-sm border flex items-center gap-3 relative"
      :class="notificationClasses"
    >
      <!-- Иконка -->
      <div class="flex-shrink-0" v-if="icon">
        <svg 
          :width="18" 
          :height="18" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2"
          class="drop-shadow-sm"
        >
          <path v-if="notification.type === 'error'" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          <path v-else-if="notification.type === 'success'" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          <path v-else-if="notification.type === 'info'" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <div class="flex-1 text-sm font-medium truncate">
        {{ notification.message }}
      </div>

      <button 
        @click="close" 
        class="btn btn-ghost btn-circle btn-xs flex-shrink-0 hover:bg-white/10 transition-colors"
        aria-label="Закрыть"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useNotification } from '~/composables/useNotification'

const { notification, close } = useNotification()
const timer = ref(null)
const isHovered = ref(false)

const notificationClasses = computed(() => {
  const base = 'border-yellow-400/30 text-slate-100 shadow-xl'
  if (notification.value.type === 'error') {
    return base + ' bg-red-500/15 border-red-500/30'
  } else if (notification.value.type === 'success') {
    return base + ' bg-green-500/15 border-green-500/30'
  } else {
    return base + ' bg-blue-500/15 border-blue-500/30'
  }
})

const icon = computed(() => {
  return ['error', 'success', 'info'].includes(notification.value.type)
})

const startTimer = () => {
  if (timer.value) clearTimeout(timer.value)
  timer.value = setTimeout(() => {
    if (!isHovered.value) close()
  }, 5000)
}

const pauseAutoClose = () => {
  isHovered.value = true
  if (timer.value) clearTimeout(timer.value)
}

const resumeAutoClose = () => {
  isHovered.value = false
  startTimer()
}

// Запускаем таймер при показе
watch(() => notification.value.show, (show) => {
  if (show) {
    startTimer()
  }
})

onUnmounted(() => {
  if (timer.value) clearTimeout(timer.value)
})
</script>

<style scoped>
.animate-fade-in {
  animation: fade-in-slide 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fade-in-slide {
  from {
    opacity: 0;
    transform: translateX(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}
</style>