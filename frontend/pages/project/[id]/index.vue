<template>
  <div>
    <Notification />
    
    <main class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Табы навигации -->
      <div class="flex gap-2 mb-6">
        <NuxtLink 
          :to="`/project/${route.params.id}`"
          class="px-5 py-3 rounded-xl font-medium relative group transition-colors"
          :class="{
            'text-yellow-200': !route.path.includes('/render'),
            'text-slate-400 hover:text-slate-200': route.path.includes('/render')
          }"
        >
          <div class="flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fde047" stroke-width="1.8">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <path d="M8 8h8" />
              <path d="M8 12h6" />
              <path d="M8 16h5" />
            </svg>
            Сценарий
          </div>
          <div 
            v-if="!route.path.includes('/render')"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-yellow-400 rounded-full"
          ></div>
        </NuxtLink>
        
        <NuxtLink
          v-if="hasScenes"
          :to="`/project/${route.params.id}/render`"
          class="px-5 py-3 rounded-xl font-medium relative group transition-colors"
          :class="{
            'text-yellow-200': route.path.includes('/render'),
            'text-slate-400 hover:text-slate-200': !route.path.includes('/render')
          }"
        >
          <div class="flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#67e8f9" stroke-width="1.8">
              <path d="M21 21H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12l4 4v10a2 2 0 0 1-2 2z" />
              <path d="M10 10l4 4-4 4" />
            </svg>
            Рендер
          </div>
          <div 
            v-if="route.path.includes('/render')"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-yellow-400 rounded-full"
          ></div>
        </NuxtLink>
      </div>
      
      <!-- Шапка проекта -->
      <div 
        class="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 mb-6 border border-slate-700/50 fade-in-up"
        style="animation-delay: 0.1s"
      >
        <input 
          v-model="project.title"
          class="w-full text-2xl font-bold mb-3 text-slate-100 placeholder-slate-500 bg-transparent border-0 focus:outline-none focus:border-yellow-400 focus:border-b-2 pb-2"
          placeholder="Название проекта"
          @blur="saveProjectMetadata"
        />
        <textarea 
          v-model="project.description"
          class="w-full text-sm text-slate-300 placeholder-slate-500 bg-transparent border-0 focus:outline-none focus:border-yellow-400 focus:border-b pb-2"
          placeholder="Ваша идея для видео..."
          rows="2"
          @blur="saveProjectMetadata"
        ></textarea>
        
                  <!-- Настройки -->
          <div class="grid md:grid-cols-3 gap-4 mt-6">
            <div class="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-slate-700/40">
              <div class="flex items-center gap-2.5 mb-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fde047" stroke-width="1.6">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M8 15h8" />
                  <path d="M9 9h1M14 9h1" />
                  <path d="M9.5 8.5a1 1 0 1 1-2 0 1 1 0 1 1 2 0z" />
                  <path d="M16.5 8.5a1 1 0 1 1-2 0 1 1 0 1 1 2 0z" />
                </svg>
                <label class="text-sm font-bold text-slate-200">Визуальный стиль</label>
              </div>
                <input
                  v-model="project.settings.tone"
                  type="text"
                  class="w-full text-slate-200 placeholder-slate-500 bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400/30 transition-colors"
                  placeholder="юмористический..."
                  :disabled="hasScenes"
                  :class="{ 'opacity-60 cursor-not-allowed': hasScenes }"
                  @blur="saveProjectMetadata"
                />
              </div>
            

            <div class="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-slate-700/40">
              <div class="flex items-center gap-2.5 mb-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#c4b5fd" stroke-width="1.6">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <circle cx="15.5" cy="8.5" r="1.5" />
                  <circle cx="8.5" cy="15.5" r="1.5" />
                  <circle cx="15.5" cy="15.5" r="1.5" />
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="12" y1="3" x2="12" y2="21" />
                </svg>
                <label class="text-sm font-bold text-slate-200">Визуальный стиль</label>
              </div>
              <input
                v-model="project.settings.style"
                type="text"
                class="w-full text-slate-200 placeholder-slate-500 bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400/30 transition-colors"
                placeholder="кинематографичный..."
                :disabled="hasScenes"
                :class="{ 'opacity-60 cursor-not-allowed': hasScenes }"
                @blur="saveProjectMetadata"
              />
            </div>

            <div class="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-slate-700/40">
              <div class="flex items-center gap-2.5 mb-3">
                <!-- Иконка: бирюзовые часы -->
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="text-cyan-400">
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12,6 12,12 16,14" />
                </svg>
                <label class="text-sm font-bold text-slate-200">Длительность (сек)</label>
              </div>
              <input
                v-model.number="project.settings.duration"
                type="number"
                class="w-full text-slate-200 placeholder-slate-500 bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400/30 transition-colors"
                placeholder="30"
                :disabled="hasScenes"
                :class="{ 'opacity-60 cursor-not-allowed': hasScenes }"
                @blur="saveProjectMetadata"
              />
            </div>
          </div>

        </div>
      
      
      

      <!-- Генерация сценария -->
      <div 
        v-if="!project.scenes || project.scenes.length === 0" 
        class="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 mb-6 text-center border border-slate-700/50 fade-in"
        style="animation-delay: 0.2s"
      >
        <div class="inline-block mb-4">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fde047" stroke-width="1.8">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-slate-100 mb-4">Генерация сценария</h2>
        <p class="mb-6 text-slate-300">
          Опишите вашу идею выше и нажмите кнопку
        </p>
        <button
          class="btn btn-van-gogh-primary px-6 py-3 rounded-xl font-medium"
          @click="handleGenerateScript"
          :disabled="generatingScript"
        >
          <span class="loading loading-spinner loading-sm" v-if="generatingScript"></span>
          {{ generatingScript ? 'Генерирую...' : 'Сгенерировать сценарий' }}
        </button>
      </div>

      <!-- Редактор сцен и картинок -->
      <div v-else class="space-y-6 fade-in" style="animation-delay: 0.2s">
        <!-- Кнопка генерации всех картинок -->
        <div 
          v-if="!hasGeneratedImages" 
          class="bg-slate-800/30 backdrop-blur-sm rounded-2xl p-6 text-center border border-slate-700/40 fade-in"
          style="animation-delay: 0.3s"
        >
          <button
            class="btn btn-van-gogh-outline px-6 py-3 rounded-xl font-medium"
            @click="generateAllImages"
            :disabled="generatingImages"
          >
            <span class="loading loading-spinner loading-sm" v-if="generatingImages"></span>
            {{ generatingImages ? 'Генерирую картинки...' : 'Сгенерировать все картинки' }}
          </button>
        </div>

        <div class="grid lg:grid-cols-2 gap-6">
          <!-- Сцены -->
          <div class="space-y-5">
            <h2 class="text-xl font-bold text-slate-100 px-1 fade-in" style="animation-delay: 0.3s">Сцены</h2>
            <SceneEditor 
              v-for="(scene, index) in project.scenes"
              :key="scene.id"
              :scene="scene"
              :is-generating-image="imageGenerationStates[scene.id]?.isGenerating"
              @update="handleUpdateScene"
              @delete="handleDeleteScene"
              @regenerate-image="handleRegenerateImage"
              class="fade-in-up"
              :style="{ animationDelay: `${0.4 + index * 0.05}s` }"
            />
          </div>
          
          <!-- Раскадровка -->
          <div>
            <h2 class="text-xl font-bold text-slate-100 mb-4 px-1 fade-in" style="animation-delay: 0.3s">Раскадровка</h2>
            <div class="space-y-5 sticky top-4">
              <ImageGenerator
                v-for="(scene, index) in project.scenes"
                :key="`image-${scene.id}`"
                :scene="scene"
                :is-generating="imageGenerationStates[scene.id]?.isGenerating"
                @regenerate="handleRegenerateImage"
                class="fade-in-up"
                :style="{ animationDelay: `${0.5 + index * 0.05}s` }"
              />

              <div 
                v-if="hasGeneratedImages" 
                class="bg-gradient-to-r from-yellow-500/10 to-blue-500/10 rounded-xl p-5 text-center border border-yellow-400/30 fade-in-up"
                style="animation-delay: 0.7s"
              >
              <div class="flex items-center justify-center gap-2 text-sm text-slate-300 mb-3">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-green-400">
                  <path d="M9 12l2 2 4-4" />
                  <circle cx="12" cy="12" r="10" />
                </svg>
                Раскадровка готова!
              </div>
                <NuxtLink
                  :to="`/project/${route.params.id}/render`"
                  class="btn btn-van-gogh-primary w-full"
                >
                  Перейти к рендеру видео
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

<style scoped>
.fade-in {
  animation: fade-in 0.5s ease-out forwards;
  opacity: 0;
}
.fade-in-up {
  animation: fade-in-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(10px);
}

@keyframes fade-in {
  to { opacity: 1; }
}
@keyframes fade-in-up {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>