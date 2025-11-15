export const useApi = () => {
  const config = useRuntimeConfig()
  const supabase = useSupabaseClient() 

  const getAuthHeader = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return {}
    return { Authorization: `Bearer ${session.access_token}` }
  }

  const apiFetch = async (endpoint, options = {}) => {
    const headers = await getAuthHeader()
    let baseUrl = config.public.apiBase
    
    if (!baseUrl.endsWith('/api/v1')) {
        if (baseUrl.endsWith('/')) {
            baseUrl = baseUrl.slice(0, -1)
        }
        baseUrl = baseUrl + '/api/v1'
    }
    
    const finalEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const fullUrl = baseUrl + finalEndpoint
    
    const response = await $fetch(fullUrl, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
      onResponseError({ response }) {
        if (response.status === 401) {
          navigateTo('/login')
        }
      }
    })

    return response
  }

  //ГЕНЕРАЦИЯ СЦЕНАРИЯ
  const generateScript = async (request) => {
    const payload = {
      prompt: request.prompt,
      genre: request.genre || null,
      style: request.style || 'cinematic',
      time: request.time || 30
    }

    try {
      return await apiFetch('/generate-script', {
        method: 'POST',
        body: payload
      })
    } catch (error) {
      console.error('Ошибка генерации сценария:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать сценарий')
    }
  }

  //ПОЛУЧЕНИЕ ПРОЕКТОВ
  const getUserProjects = async () => {
    try {
      console.log('[useApi] Calling getUserProjects')
      const result = await apiFetch('/projects')
      console.log('[useApi] getUserProjects result:', result)
      return result
    } catch (error) {
      console.error('[useApi] getUserProjects error:', error)
      throw error
    }
  }

  //ПОЛУЧЕНИЕ ПРОЕКТА
  const getProject = async (id) => {
    return await apiFetch(`/projects/${id}`)
  }

  //ГЕНЕРАЦИЯ ВСЕХ ИЗОБРАЖЕНИЙ
  const generateImages = async (projectId) => {
    try {
      return await apiFetch(`/generate-image/${projectId}`, {
        method: 'POST'
      })
    } catch (error) {
      console.error('Ошибка генерации изображений:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать изображения')
    }
  }

  //ОБНОВЛЕНИЕ СЦЕНЫ
  const updateScene = async (sceneId, updates) => {
    try {
      return await apiFetch(`/scenes/${sceneId}`, {
        method: 'PUT',
        body: updates
      })
    } catch (error) {
      console.error('Ошибка обновления сцены:', error)
      throw new Error(error.data?.detail || 'Не удалось обновить сцену')
    }
  }

  //ПЕРЕГЕНЕРАЦИЯ СЦЕНЫ
  const regenerateScene = async (sceneId, style = null) => {
    try {
      const body = style ? { style } : {}
      return await apiFetch(`/regenerate-scene/${sceneId}`, {
        method: 'POST',
        body
      })
    } catch (error) {
      console.error('Ошибка перегенерации сцены:', error)
      throw new Error(error.data?.detail || 'Не удалось перегенерировать изображение')
    }
  }

  //ОБНОВЛЕНИЕ МЕТАДАННЫХ ПРОЕКТА
  const updateProject = async (projectId, updates) => {
    try {
      return await apiFetch(`/projects/${projectId}`, {
        method: 'PUT',
        body: updates
      })
    } catch (error) {
      console.error('Ошибка обновления проекта:', error)
      throw new Error(error.data?.detail || 'Не удалось обновить проект')
    }
  }

  //УДАЛЕНИЕ СЦЕНЫ
  const deleteScene = async (sceneId) => {
    try {
      return await apiFetch(`/scenes/${sceneId}`, {
        method: 'DELETE'
      })
    } catch (error) {
      console.error('Ошибка удаления сцены:', error)
      throw new Error(error.data?.detail || 'Не удалось удалить сцену')
    }
  }

  //УДАЛЕНИЕ ПРОЕКТА
  const deleteProject = async (projectId) => {
    try {
      return await apiFetch(`/projects/${projectId}`, {
        method: 'DELETE'
      })
    } catch (error) {
      console.error('Ошибка удаления проекта:', error)
      throw new Error(error.data?.detail || 'Не удалось удалить проект')
    }
  }

  //РЕНДЕРИНГ
  const generateVoiceover = async (projectId) => {
    try {
      console.log('[useApi] Calling generateVoiceover for project:', projectId)
      const result = await apiFetch(`/generate-voiceover/${projectId}`, {
        method: 'POST'
      })
      console.log('[useApi] generateVoiceover result:', result)
      return result
    } catch (error) {
      console.error('[useApi] generateVoiceover error:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать озвучку')
    }
  }

  const startRender = async (projectId, settings) => {
    try {
      console.log('[useApi] Calling startRender for project:', projectId, 'settings:', settings)
      const result = await apiFetch(`/render-video/${projectId}`, {
        method: 'POST',
        body: settings
      })
      console.log('[useApi] startRender result:', result)
      return result
    } catch (error) {
      console.error('[useApi] startRender error:', error)
      throw new Error(error.data?.detail || 'Не удалось запустить рендеринг')
    }
  }

  const getRenderStatus = async (projectId) => {
    try {
      return await apiFetch(`/render-status/${projectId}`)
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось получить статус')
    }
  }

  return {
    generateScript,
    getUserProjects,
    getProject,
    generateImages,
    updateScene,
    regenerateScene,
    updateProject,
    deleteScene,
    deleteProject,
    generateVoiceover,
    startRender,
    getRenderStatus
  }
}