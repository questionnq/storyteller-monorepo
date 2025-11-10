export const useVideo = () => {
  const videoUrl = ref(null)
  const status = ref('pending') // pending, processing, done, failed
  const error = ref(null)
  
  const startRender = async (projectId, settings) => {
    status.value = 'processing'
    try {
      await $fetch(`/api/v1/projects/${projectId}/render`, {
        method: 'POST',
        body: settings
      })
      // Начинаем опрос статуса
      pollStatus(projectId)
    } catch (err) {
      status.value = 'failed'
      error.value = err.message
    }
  }
  
  const pollStatus = async (projectId) => {
    const { start, stop } = usePolling(async () => {
      const result = await $fetch(`/api/v1/projects/${projectId}/status`)
      status.value = result.status
      
      if (result.status === 'done') {
        videoUrl.value = result.video_url
        stop()
      } else if (result.status === 'failed') {
        error.value = result.error
        stop()
      }
    }, 2000)
    
    start()
  }
  
  return {
    videoUrl,
    status,
    error,
    startRender
  }
}