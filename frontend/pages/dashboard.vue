<template>
  <div>
    <Notification />
    
    <main class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Шапка -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-4xl font-bold">Мои проекты</h1>
        <button 
          class="btn btn-primary btn-lg"
          @click="createNewProject"
        >
          ➕ Новый проект
        </button>
      </div>

      <!-- Ошибка загрузки -->
      <div v-if="error" class="alert alert-error mb-6">
        <span>❌ {{ error }}</span>
      </div>

      <!-- Список проектов -->
      <div v-if="!loading && projects.length > 0" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProjectCard 
          v-for="project in projects"
          :key="project.id"
          :project="project"
          @click="openProject(project.id)"
          @delete="deleteProject(project.id)"
        />
      </div>

      <!-- Пустое состояние -->
      <div v-else-if="!loading && projects.length === 0" class="bg-base-200 rounded-lg p-12 text-center">
        <div class="text-6xl mb-4">🎬</div>
        <h2 class="text-2xl font-bold mb-4">У вас пока нет проектов</h2>
        <p class="mb-6 opacity-70">
          Создайте свой первый проект и начните создавать сценарии
        </p>
        <button 
          class="btn btn-primary btn-lg"
          @click="createNewProject"
        >
          Создать проект
        </button>
      </div>

      <!-- Лоадер -->
      <div v-else class="flex justify-center items-center h-64">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
    </main>
  </div>
</template>

<script setup>
const { getUserProjects, deleteProject: apiDeleteProject } = useApi()
const { showError, showSuccess } = useNotification()
const router = useRouter()

const projects = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  await loadProjects()
})

const loadProjects = async () => {
  loading.value = true
  error.value = null
  
  try {
    projects.value = await getUserProjects()
  } catch (err) {
    error.value = err.message || 'Не удалось загрузить проекты'
    showError(error.value)
  } finally {
    loading.value = false
  }
}

const createNewProject = () => {
  router.push('/project/new')
}

const openProject = (id) => {
  router.push(`/project/${id}`)
}

const deleteProject = async (id) => {
  if (!confirm('Удалить проект? Это действие нельзя отменить.')) return
  
  try {
    await apiDeleteProject(id)
    showSuccess('Проект удалён')
    await loadProjects()
  } catch (err) {
    showError('Не удалось удалить проект: ' + err.message)
  }
}
</script>