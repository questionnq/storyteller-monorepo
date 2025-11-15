export const useAudio = () => {
  const audioUrl = ref(null)
  const subtitles = ref(null)
  const isGenerating = ref(false)
  
  const generateVoiceover = async (projectId, scenes) => {
    isGenerating.value = true
    try {
      const result = await $fetch(`/api/v1/projects/${projectId}/voiceover`, {
        method: 'POST',
        body: { scenes }
      })
      audioUrl.value = result.audio_url
      subtitles.value = result.subtitles
    } catch (error) {
      console.error('Voiceover error:', error)
      throw error
    } finally {
      isGenerating.value = false
    }
  }
  
  return {
    audioUrl,
    subtitles,
    isGenerating,
    generateVoiceover
  }
}