<template>
  <div v-if="notification.show" class="fixed top-4 right-4 z-50">
    <div class="alert shadow-lg" :class="alertClass">
      <div class="flex items-center gap-2">
        <span v-if="notification.type === 'error'">❌</span>
        <span v-if="notification.type === 'success'">✅</span>
        <span v-if="notification.type === 'info'">ℹ️</span>
        <span>{{ notification.message }}</span>
      </div>
      <button @click="close" class="btn btn-ghost btn-xs">
        ✕
      </button>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useNotification } from '~/composables/useNotification'

const { notification, close } = useNotification()

const alertClass = computed(() => {
  return {
    'alert-error': notification.value.type === 'error',
    'alert-success': notification.value.type === 'success',
    'alert-info': notification.value.type === 'info'
  }
})

// Автоматически скрываем через 5 секунд
watch(() => notification.value.show, (show) => {
  if (show) {
    setTimeout(() => {
      close()
    }, 5000)
  }
})
</script>