// composables/useApi.js
import { z } from 'zod'

// Схемы валидации ответов
const SceneSchema = z.object({
  scene_number: z.number(),
  action: z.string(),
  dialogues: z.array(z.string()).optional(),
  voiceover: z.string().optional(),
  notes: z.string().optional(),
  duration: z.number().optional()
})

const ScriptSchema = z.object({
  title: z.string(),
  description: z.string(),
  tone: z.string(),
  target_audience: z.string().optional(),
  scenes: z.array(SceneSchema)
})

const ImageGenerationSchema = z.object({
  scene_id: z.number(),
  image_url: z.string(),
  prompt: z.string(),
  style: z.string()
})

export const useApi = () => {
  const config = useRuntimeConfig()
  const { user } = useSupabaseAuth()
  
  const getAuthHeader = async () => {
    if (!user.value) return {}
    const token = await user.value.getIdToken()
    return { Authorization: `Bearer ${token}` }
  }

  const apiFetch = async (endpoint, options = {}) => {
    const headers = await getAuthHeader()
    
    return $fetch(`${config.public.apiBase}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
        ...options.headers
      }
    })
  }

  // Генерация сценария
  const generateScript = async (idea, options = {}) => {
    try {
      return await apiFetch('/script/generate', {
        method: 'POST',
        body: {
          idea,
          tone: options.tone || 'neutral',
          duration: options.duration || 30,
          style: options.style || 'cinematic',
          target_audience: options.targetAudience || 'general'
        }
      })
    } catch (error) {
      console.error('Ошибка генерации сценария:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать сценарий')
    }
  }

  // Генерация изображения для сцены
  const generateSceneImage = async (scene, style = 'cinematic') => {
    try {
      return await apiFetch('/image/generate', {
        method: 'POST',
        body: {
          scene_description: scene.action,
          style,
          scene_number: scene.scene_number
        }
      })
    } catch (error) {
      console.error('Ошибка генерации изображения:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать изображение')
    }
  }

  // Сохранение проекта
  const saveProject = async (projectData) => {
    return await apiFetch('/projects', {
      method: 'POST',
      body: projectData
    })
  }

  // Получение проектов пользователя
  const getUserProjects = async () => {
    return await apiFetch('/projects')
  }

  // Получение конкретного проекта
  const getProject = async (id) => {
    return await apiFetch(`/projects/${id}`)
  }

  // Генерация озвучки
  const generateVoiceover = async (projectId, scenes) => {
    try {
      return await apiFetch(`/projects/${projectId}/voiceover`, {
        method: 'POST',
        body: { scenes }
      })
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось сгенерировать озвучку')
    }
  }
  
  // Запуск рендеринга видео
  const startRender = async (projectId, settings) => {
    try {
      return await apiFetch(`/projects/${projectId}/render`, {
        method: 'POST',
        body: settings
      })
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось запустить рендеринг')
    }
  }
  
  // Получение статуса рендеринга
  const getRenderStatus = async (projectId) => {
    try {
      return await apiFetch(`/projects/${projectId}/status`)
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось получить статус')
    }
  }


  return {
    generateScript,
    generateSceneImage,
    saveProject,
    getUserProjects,
    getProject,
    generateVoiceover,
    startRender,
    getRenderStatus
  }
}