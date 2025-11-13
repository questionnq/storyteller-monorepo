<template>
  <div>
    <Notification />
    
    <main class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Табы навигации -->
      <div class="tabs tabs-boxed mb-6">
        <NuxtLink 
          :to="`/project/${route.params.id}`"
          class="tab"
          :class="{ 'tab-active': !route.path.includes('/render') }"
        >
          📋 Сценарий
        </NuxtLink>
        
        <NuxtLink
          v-if="hasScenes"
          :to="`/project/${route.params.id}/render`"
          class="tab"
          :class="{ 'tab-active': route.path.includes('/render') }"
        >
          🎬 Рендер
        </NuxtLink>
      </div>
      
      <!-- Шапка проекта -->
      <div class="bg-base-200 rounded-lg p-5 mb-6 shadow-lg">
        <input 
          v-model="project.title"
          class="input input-ghost text-2xl font-bold w-full mb-3"
          placeholder="Название проекта"
          @blur="saveProjectMetadata"
        />
        <textarea 
          v-model="project.description"
          class="textarea textarea-ghost w-full text-sm"
          placeholder="Ваша идея для видео..."
          rows="2"
          @blur="saveProjectMetadata"
        ></textarea>
        
        <!-- Настройки -->
        <div class="grid md:grid-cols-3 gap-4 mt-5">
          <div class="bg-base-100 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🎯</span>
              <label class="text-sm font-bold">Тон сценария</label>
            </div>
            <input
              v-model="project.settings.tone"
              type="text"
              class="input input-bordered w-full"
              placeholder="юмористический..."
              :disabled="hasScenes"
              :class="{ 'opacity-60 cursor-not-allowed': hasScenes }"
              @blur="saveProjectMetadata"
            />
          </div>

          <div class="bg-base-100 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🎨</span>
              <label class="text-sm font-bold">Визуальный стиль</label>
            </div>
            <input
              v-model="project.settings.style"
              type="text"
              class="input input-bordered w-full"
              placeholder="кинематографичный..."
              :disabled="hasScenes"
              :class="{ 'opacity-60 cursor-not-allowed': hasScenes }"
              @blur="saveProjectMetadata"
            />
          </div>

          <div class="bg-base-100 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">⏱️</span>
              <label class="text-sm font-bold">Длительность (сек)</label>
            </div>
            <input
              v-model.number="project.settings.duration"
              type="number"
              class="input input-bordered w-full"
              placeholder="30"
              :disabled="hasScenes"
              :class="{ 'opacity-60 cursor-not-allowed': hasScenes }"
              @blur="saveProjectMetadata"
            />
          </div>
        </div>
      </div>
      
      <!-- Генерация сценария -->
      <div v-if="!project.scenes || project.scenes.length === 0" class="bg-base-200 rounded-lg p-8 mb-6 text-center">
        <div class="text-6xl mb-4">✨</div>
        <h2 class="text-2xl font-bold mb-4">Генерация сценария</h2>
        <p class="mb-6 opacity-70">
          Опишите вашу идею выше и нажмите кнопку
        </p>
        <button
          class="btn btn-primary btn-lg"
          @click="handleGenerateScript"
          :disabled="generatingScript"
        >
          <span class="loading loading-spinner" v-if="generatingScript"></span>
          {{ generatingScript ? 'Генерирую...' : '📝 Сгенерировать сценарий' }}
        </button>
      </div>

      <!-- Редактор сцен и картинок -->
      <div v-else class="space-y-6">
        <!-- Кнопка генерации всех картинок (если еще не сгенерированы) -->
        <div v-if="!hasGeneratedImages" class="bg-base-200 rounded-lg p-6 text-center">
          <button
            class="btn btn-secondary btn-lg"
            @click="generateAllImages"
            :disabled="generatingImages"
          >
            <span class="loading loading-spinner" v-if="generatingImages"></span>
            {{ generatingImages ? 'Генерирую картинки...' : '🎨 Сгенерировать все картинки' }}
          </button>
        </div>

        <div class="grid lg:grid-cols-2 gap-6">
        <!-- Левая колонка: Сцены -->
        <div class="space-y-5">
          <h2 class="text-xl font-bold px-1">📋 Сцены</h2>
          <SceneEditor 
            v-for="scene in project.scenes"
            :key="scene.id"
            :scene="scene"
            :is-generating-image="imageGenerationStates[scene.id]?.isGenerating"
            @update="handleUpdateScene"
            @delete="handleDeleteScene"
            @regenerate-image="handleRegenerateImage"
          />
        </div>
        
        <!-- Правая колонка: Картинки -->
        <div>
          <h2 class="text-xl font-bold mb-4 px-1">🖼️ Раскадровка</h2>
          <div class="space-y-5 sticky top-4">
            <ImageGenerator
              v-for="scene in project.scenes"
              :key="`image-${scene.id}`"
              :scene="scene"
              :is-generating="imageGenerationStates[scene.id]?.isGenerating"
              @regenerate="handleRegenerateImage"
            />

            <!-- Кнопка перехода на рендер -->
            <div v-if="hasGeneratedImages" class="bg-primary/10 rounded-lg p-4 text-center border-2 border-primary/20">
              <p class="text-sm mb-3 opacity-80">✅ Раскадровка готова!</p>
              <NuxtLink
                :to="`/project/${route.params.id}/render`"
                class="btn btn-primary btn-block"
              >
                🎬 Перейти к рендеру видео
              </NuxtLink>
            </div>
          </div>
        </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const {
  generateScript: apiGenerateScript,
  generateImages: apiGenerateImages,
  updateScene: apiUpdateScene,
  regenerateScene: apiRegenerateScene,
  updateProject: apiUpdateProject,
  getProject: apiGetProject,
  deleteScene: apiDeleteScene
} = useApi()
const { requireAuth } = useSupabaseAuth()
const { showError, showSuccess } = useNotification()
const { confirm } = useConfirm()
const route = useRoute()
const router = useRouter()

const project = ref({
  id: null,
  title: 'Новый проект',
  description: '',
  intro: '',
  settings: {
    tone: '',
    style: '',
    duration: 30
  },
  scenes: []
})

const imageGenerationStates = ref({})
const generatingScript = ref(false)
const generatingImages = ref(false)

const hasScenes = computed(() => {
  return project.value.scenes && project.value.scenes.length > 0
})

const hasGeneratedImages = computed(() => {
  return project.value.scenes &&
         project.value.scenes.some(scene => scene.generated_image_url)
})

onMounted(async () => {
  await requireAuth()
  if (route.params.id !== 'new') {
    await loadProject(route.params.id)
  }
})

const loadProject = async (id) => {
  try {
    const response = await apiGetProject(id)
    
    project.value = {
      id: response.id,
      title: response.title || 'Проект',
      description: response.description || '',
      intro: response.intro || '',
      settings: response.settings || { tone: '', style: '', duration: 30 },
      scenes: response.scenes || []
    }
  } catch (err) {
    showError('Ошибка загрузки проекта: ' + err.message)
  }
}

const handleGenerateScript = async () => {
  if (!project.value.description.trim()) {
    showError('Опишите вашу идею для видео')
    return
  }

  generatingScript.value = true
  try {
    const result = await apiGenerateScript({
      prompt: project.value.description,
      genre: project.value.settings.tone || 'neutral',
      style: project.value.settings.style || 'cinematic',
      time: project.value.settings.duration || 30
    })

    if (result?.project_id) {
      await router.replace(`/project/${result.project_id}`)
      await loadProject(result.project_id)
      showSuccess('Сценарий сгенерирован!')
    }
  } catch (error) {
    showError('Ошибка генерации сценария: ' + error.message)
  } finally {
    generatingScript.value = false
  }
}

const generateAllImages = async () => {
  if (!project.value.scenes || project.value.scenes.length === 0) return
  
  generatingImages.value = true
  
  try {
    const result = await apiGenerateImages(project.value.id)
    
    result.scenes.forEach(sceneData => {
      const scene = project.value.scenes.find(s => s.id === sceneData.scene_id)
      if (scene) {
        scene.generated_image_url = sceneData.generated_image_url
      }
    })
    
    showSuccess('Все картинки сгенерированы!')
  } catch (error) {
    showError('Ошибка генерации картинок: ' + error.message)
  } finally {
    generatingImages.value = false
  }
}

const handleUpdateScene = async (updatedScene) => {
  try {
    await apiUpdateScene(updatedScene.id, {
      action: updatedScene.action,
      dialogue: updatedScene.dialogue,
      voice_over: updatedScene.voice_over,
      visual_prompt: updatedScene.visual_prompt
    })
    
    const index = project.value.scenes.findIndex(s => s.id === updatedScene.id)
    if (index !== -1) {
      project.value.scenes[index] = { ...project.value.scenes[index], ...updatedScene }
    }
  } catch (error) {
    showError('Ошибка обновления сцены: ' + error.message)
  }
}

const handleDeleteScene = async (sceneId) => {
  console.log('[handleDeleteScene] Starting deletion for scene:', sceneId)

  const confirmed = await confirm(
    'Удалить сцену?',
    'Это действие нельзя отменить. Сцена будет удалена из проекта.'
  )

  console.log('[handleDeleteScene] Confirmed:', confirmed)
  if (!confirmed) return

  try {
    console.log('[handleDeleteScene] Calling apiDeleteScene...')
    const result = await apiDeleteScene(sceneId)
    console.log('[handleDeleteScene] API result:', result)

    project.value.scenes = project.value.scenes.filter(s => s.id !== sceneId)

    project.value.scenes.forEach((scene, index) => {
      scene.scene_number = index + 1
    })

    console.log('[handleDeleteScene] Scenes after deletion:', project.value.scenes.length)
    showSuccess('Сцена удалена')
  } catch (error) {
    console.error('[handleDeleteScene] Error:', error)
    showError('Ошибка удаления сцены: ' + error.message)
  }
}

const handleRegenerateImage = async ({ sceneId, style }) => {
  const scene = project.value.scenes.find(s => s.id === sceneId)
  if (!scene) return

  imageGenerationStates.value[sceneId] = { isGenerating: true }
  
  try {
    const result = await apiRegenerateScene(sceneId, style || null)
    
    scene.generated_image_url = result.generated_image_url
    showSuccess(`Изображение сцены ${scene.scene_number} обновлено!`)
  } catch (error) {
    showError(`Ошибка генерации изображения: ${error.message}`)
  } finally {
    imageGenerationStates.value[sceneId].isGenerating = false
  }
}

const saveProjectMetadata = async () => {
  if (!project.value.id) return
  
  try {
    await apiUpdateProject(project.value.id, {
      title: project.value.title,
      description: project.value.description,
      tone: project.value.settings.tone,
      style: project.value.settings.style,
      project_time: project.value.settings.duration
    })
  } catch (error) {
    showError('Ошибка сохранения: ' + error.message)
  }
}
</script>