<template>
  <div>
    <AppHeader />
    
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">Мои проекты</h1>
        <button class="btn btn-primary" @click="handleCreateProject">
          + Новый проект
        </button>
      </div>

      <!-- Состояние загрузки -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="i in 3" :key="i" class="card bg-base-200 shadow-xl">
          <div class="card-body">
            <div class="skeleton h-6 w-3/4 mb-2"></div>
            <div class="skeleton h-4 w-full mb-4"></div>
            <div class="skeleton h-10 w-full"></div>
          </div>
        </div>
      </div>

      <!-- Список проектов -->
      <div v-else-if="projects.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div 
          v-for="project in projects" 
          :key="project.id"
          class="card bg-base-200 shadow-xl hover:shadow-2xl transition-all"
        >
          <div class="card-body">
            <div class="flex justify-between items-start mb-2">
              <h3 class="card-title text-lg">{{ project.title }}</h3>
              <span 
                class="badge badge-sm"
                :class="{
                  'badge-warning': !project.script,
                  'badge-info': project.script && !project.final_video_url,
                  'badge-success': project.final_video_url
                }"
              >
                {{ project.final_video_url ? 'Готов' : project.script ? 'В процессе' : 'Черновик' }}
              </span>
            </div>
            
            <p class="text-sm opacity-70 line-clamp-2 mb-4">{{ project.description }}</p>
            
            <div class="flex gap-2">
              <NuxtLink 
                :to="`/project/${project.id}`"
                class="btn btn-primary btn-sm flex-1"
              >
                Открыть
              </NuxtLink>
              
              <NuxtLink 
                v-if="project.script"
                :to="`/project/${project.id}/render`"
                class="btn btn-secondary btn-sm"
              >
                Рендер
              </NuxtLink>
            </div>
            
            <div class="text-xs opacity-50 mt-3">
              {{ formatDate(project.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Пустое состояние -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4 opacity-30">🎬</div>
        <h2 class="text-2xl font-bold mb-4">У вас пока нет проектов</h2>
        <p class="mb-6 opacity-70">Создайте ваш первый проект и начните генерировать сценарии</p>
        <button class="btn btn-primary btn-lg" @click="handleCreateProject">
          Создать проект
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
const { getUserProjects, saveProject } = useApi()
const { requireAuth } = useSupabaseAuth()
const router = useRouter()

const loading = ref(true)
const projects = ref([])

onMounted(async () => {
  requireAuth()
  await loadProjects()
})

const loadProjects = async () => {
  try {
    loading.value = true
    projects.value = await getUserProjects()
  } catch (error) {
    console.error('Ошибка загрузки проектов:', error)
  } finally {
    loading.value = false
  }
}

// ✅ ПРОВЕРЕННАЯ ФУНКЦИЯ СОЗДАНИЯ ПРОЕКТА
const handleCreateProject = async () => {
  try {
    const newProject = {
      title: 'Новый проект',
      description: '',
      settings: { tone: '', style: '' },
      script: null,
      images: {},
      imagePrompts: {}
    }
    
    const created = await saveProject(newProject)
    if (created?.id) {
      router.push(`/project/${created.id}`)
    } else {
      throw new Error('ID проекта не получен')
    }
  } catch (error) {
    console.error('Ошибка создания проекта:', error)
    alert(`Не удалось создать проект: ${error.message}`)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}
</script>