import { ref, onUnmounted } from 'vue'

export const usePolling = (callback, interval = 2000) => {
  const isPolling = ref(false)
  const intervalId = ref(null)
  
  const start = () => {
    if (isPolling.value) return
    
    isPolling.value = true
    intervalId.value = setInterval(async () => {
      try {
        await callback()
      } catch (error) {
        console.error('Polling error:', error)
        stop()
      }
    }, interval)
  }
  
  const stop = () => {
    if (intervalId.value) {
      clearInterval(intervalId.value)
      intervalId.value = null
    }
    isPolling.value = false
  }
  
  onUnmounted(() => {
    stop()
  })
  
  return {
    isPolling,
    start,
    stop
  }
}