<template>
  <div>
    <AppHeader />
    
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
          v-if="hasGeneratedImages"
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
          @blur="saveProject"
        />
        <textarea 
          v-model="project.description"
          class="textarea textarea-ghost w-full text-sm"
          placeholder="Ваша идея для видео..."
          rows="2"
          @blur="saveProject"
        ></textarea>
        
        <!-- Настройки (пофикшено наложение) -->
        <div class="grid md:grid-cols-2 gap-6 mt-5">
          <!-- Тон сценария -->
          <div class="bg-base-100 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🎯</span>
              <label class="text-sm font-bold">Тон сценария</label>
            </div>
            <input 
              v-model="project.settings.tone"
              type="text"
              class="input input-bordered w-full"
              placeholder="Например: юмористический, драматичный, мотивирующий"
              @blur="saveProject"
            />
            <p class="text-xs opacity-60 mt-2">
              Каким должен быть характер текста
            </p>
          </div>
          
          <!-- Визуальный стиль -->
          <div class="bg-base-100 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🎨</span>
              <label class="text-sm font-bold">Визуальный стиль</label>
            </div>
            <input 
              v-model="project.settings.style"
              type="text"
              class="input input-bordered w-full"
              placeholder="Например: кинематографичный, мультфильм, реалистичный"
              @blur="saveProject"
            />
            <p class="text-xs opacity-60 mt-2">
              Как должны выглядеть картинки
            </p>
          </div>
        </div>
      </div>
      
      <!-- Генерация сценария -->
      <div v-if="!project.script" class="bg-base-200 rounded-lg p-8 mb-6 text-center">
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
      
      <!-- Блок генерации картинок -->
      <div v-else-if="!hasGeneratedImages" class="bg-base-200 rounded-lg p-8 mb-6 text-center">
        <div class="text-5xl mb-3">🎨</div>
        <h3 class="text-xl font-bold mb-2">Следующий шаг: картинки</h3>
        <p class="opacity-70 mb-4">
          Сгенерируйте визуальную раскадровку для ваших сцен
        </p>
        <button 
          class="btn btn-secondary"
          @click="generateAllImages"
          :disabled="generatingImages"
        >
          <span class="loading loading-spinner" v-if="generatingImages"></span>
          {{ generatingImages ? 'Генерирую...' : 'Сгенерировать все картинки' }}
        </button>
      </div>
      
      <!-- Редактор сцен и картинок -->
      <div v-else class="grid lg:grid-cols-2 gap-6">
        <div class="space-y-5">
          <h2 class="text-xl font-bold px-1">📋 Сцены</h2>
          <SceneEditor 
            v-for="scene in project.script.scenes"
            :key="scene.scene_number"
            :scene="scene"
            :is-generating-image="imageGenerationStates[scene.scene_number]?.isGenerating"
            @update="updateScene"
            @delete="deleteScene(scene.scene_number)"
            @regenerate-image="handleRegenerateSingleImage"
          />
        </div>
        
        <div>
          <h2 class="text-xl font-bold mb-4 px-1">🖼️ Раскадровка</h2>
          <div class="space-y-5 max-h-screen overflow-y-auto">
            <ImageGenerator
              v-for="scene in project.script.scenes"
              :key="`image-${scene.scene_number}`"
              :scene-number="scene.scene_number"
              :image-url="project.images[scene.scene_number]"
              :prompt="project.imagePrompts[scene.scene_number]"
              :is-generating="imageGenerationStates[scene.scene_number]?.isGenerating"
              @regenerate="handleRegenerateSingleImage"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const { generateScript: apiGenerateScript, generateSceneImage, saveProject: apiSaveProject, getProject } = useApi()
const { requireAuth } = useSupabaseAuth()
const route = useRoute()
const router = useRouter()

const project = ref({
  title: 'Новый проект',
  description: '',
  settings: {
    tone: '',
    style: ''
  },
  script: null,
  images: {},
  imagePrompts: {}
})

const imageGenerationStates = ref({})
const generatingScript = ref(false)
const generatingImages = ref(false)

const hasGeneratedImages = computed(() => {
  return project.value.script && 
         project.value.images && 
         Object.keys(project.value.images).length > 0
})

onMounted(async () => {
  if (route.params.id !== 'new') {
    await loadProject(route.params.id)
  }
})

const loadProject = async (id) => {
  try {
    const loadedProject = await getProject(id)
    project.value = {
      ...loadedProject,
      settings: loadedProject.settings || { tone: '', style: '' }
    }
  } catch (error) {
    console.error('Ошибка загрузки проекта:', error)
  }
}

const handleGenerateScript = async () => {
  if (!project.value.description.trim()) {
    alert('Опишите вашу идею для видео')
    return
  }

  generatingScript.value = true
  
  try {
    const result = await apiGenerateScript(project.value.description, {
      tone: project.value.settings.tone,
      targetAudience: 'general'
    })
    
    project.value.script = result.script
    project.value.title = result.script.title || project.value.title
    
    project.value.images = {}
    project.value.imagePrompts = {}
    
    await saveProject()
  } catch (error) {
    alert(error.message)
  } finally {
    generatingScript.value = false
  }
}

const generateAllImages = async () => {
  if (!project.value.script?.scenes) return
  
  generatingImages.value = true
  
  try {
    for (const scene of project.value.script.scenes) {
      await handleRegenerateSingleImage({ sceneNumber: scene.scene_number })
    }
  } catch (error) {
    alert('Ошибка генерации картинок: ' + error.message)
  } finally {
    generatingImages.value = false
  }
}

const updateScene = (updatedScene) => {
  const index = project.value.script.scenes.findIndex(s => s.scene_number === updatedScene.scene_number)
  if (index !== -1) {
    project.value.script.scenes[index] = updatedScene
    saveProject()
  }
}

const deleteScene = (sceneNumber) => {
  if (!confirm('Удалить сцену?')) return
  
  project.value.script.scenes = project.value.script.scenes.filter(s => s.scene_number !== sceneNumber)
  project.value.script.scenes.forEach((scene, index) => {
    scene.scene_number = index + 1
  })
  saveProject()
}

const handleRegenerateSingleImage = async ({ sceneNumber, style }) => {
  const scene = project.value.script.scenes.find(s => s.scene_number === sceneNumber)
  if (!scene) return

  imageGenerationStates.value[sceneNumber] = { isGenerating: true }
  
  try {
    const result = await generateSceneImage(scene, style || project.value.settings.style)
    project.value.images[sceneNumber] = result.image_url
    project.value.imagePrompts[sceneNumber] = result.prompt
  } catch (error) {
    alert(`Ошибка генерации изображения: ${error.message}`)
  } finally {
    imageGenerationStates.value[sceneNumber].isGenerating = false
    saveProject()
  }
}

const saveProject = async () => {
  try {
    const result = await apiSaveProject(project.value)
    if (route.params.id === 'new' && result.id) {
      router.replace(`/project/${result.id}`)
    }
  } catch (error) {
    console.error('Ошибка сохранения проекта:', error)
  }
}
</script>