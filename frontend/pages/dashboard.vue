<template>
  <div 
    class="min-h-screen relative overflow-hidden"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- Van Gogh-текстура (гарантированно работает) -->
    <div 
      class="absolute inset-0 z-0"
      :style="{ 
        backgroundImage: `url('${brushTexture}')`,
        backgroundSize: '300px 300px',
        opacity: 0.9
      }"
    ></div>

    <!-- Параллакс-облака -->
    <div 
      class="absolute w-96 h-44 rounded-full opacity-8 z-0"
      :style="{
        background: 'radial-gradient(circle, rgba(253, 224, 71, 0.1) 0%, transparent 70%)',
        top: `${cloud1.y}px`,
        left: `${cloud1.x}px`,
        transform: `scale(${1 + mouseIntensity * 0.15})`
      }"
    ></div>
    <div 
      class="absolute w-80 h-40 rounded-full opacity-7 z-0"
      :style="{
        background: 'radial-gradient(circle, rgba(139, 92, 246, 0.09) 0%, transparent 70%)',
        top: `${cloud2.y}px`,
        left: `${cloud2.x}px`,
        transform: `scale(${1 + mouseIntensity * 0.1})`
      }"
    ></div>

    <!-- Свечение под курсором -->
    <div 
      class="absolute inset-0 z-0 opacity-25"
      :style="{
        background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(253, 224, 71, 0.12) 0%, transparent 60%)`
      }"
    ></div>

    <!-- Контент -->
    <main class="container mx-auto px-4 py-8 max-w-7xl relative z-10">
      <Notification />

      <div class="flex justify-between items-center mb-10">
        <h1 class="text-3xl font-bold text-slate-100">Мои проекты</h1>
        <button 
          class="btn btn-van-gogh-primary px-6 py-3 rounded-xl font-medium flex items-center gap-2"
          @click="createNewProject"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Новый проект
        </button>
      </div>

      <div v-if="error" class="mb-6 p-4 rounded-xl bg-red-900/30 border border-red-500/40 text-red-200">
        {{ error }}
      </div>

      <div v-if="!loading && projects.length > 0" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProjectCard 
          v-for="(project, index) in projects"
          :key="project.id"
          :project="project"
          :is-loading="loading"
          @delete="deleteProject(project.id)"
          class="project-item"
          :style="{ animationDelay: `${Math.min(0.5, index * 0.05)}s` }"
        />
      </div>

      <div v-else-if="!loading && projects.length === 0" class="fade-in-up">
        <div class="bg-slate-800/30 backdrop-blur-sm border border-slate-700/40 rounded-2xl p-12 text-center max-w-2xl mx-auto">
          <div class="inline-block mb-6">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" class="text-yellow-400/60">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-slate-100 mb-3">Пока нет проектов</h2>
          <p class="text-slate-300 mb-6">
            Создайте свой первый проект — и начните превращать идеи в сториборды и видео.
          </p>
          <button 
            class="btn btn-van-gogh-primary px-6 py-3 rounded-xl font-medium mx-auto flex items-center gap-2"
            @click="createNewProject"
          >
            Создать проект
          </button>
        </div>
      </div>

      <!-- Van Gogh-лоадер -->
      <div v-else class="flex flex-col items-center justify-center h-64 fade-in">
        <div class="loading-spinner mb-4">
          <div class="loading-inner"></div>
        </div>
        <p class="text-slate-300">Загрузка проектов...</p>
      </div>
    </main>
  </div>
</template>

<script setup>
const { getUserProjects, deleteProject: apiDeleteProject } = useApi()
const { showError, showSuccess } = useNotification()
const { confirm } = useConfirm()
const router = useRouter()

const projects = ref([])
const loading = ref(true)
const error = ref(null)

// Van Gogh brush texture (base64, 100% рабочий)
const brushTexture = `data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMDAgMzAwIj48ZyBmaWxsPSJub25lIj48cGF0aCBkPSJNNDAsODAgUTcwLDQwIDEyMCw3MCBRMTYwLDkwIDE5MCw2MCIgc3Ryb2tlPSJyZ2JhKDI1MywyMjQsMTE1LDAuMDgpIiBzdHJva2Utd2lkdGg9IjIiIG9wYWNpdHk9IjAuNiIvPjxwYXRoIGQ9Ik0yMCwxNTAgUTYwLDEyMCAxMDAsMTYwIFEyMDAsMTgwIDE4MCwxNDAiIHN0cm9rZT0icmdiYSgxMzksOTIsMjQ2LDAuMDYpIiBzdHJva2Utd2lkdGg9IjEuNSIgb3BhY2l0eT0iMC41Ii8+PHBhdGggZD0iTTYwLDIyMCBRMTAwLDIwMCAxNDAsMjMwIFE1MCwyNTAgMjIwLDIyMCIgc3Ryb2tlPSJyZ2JhKDU2LDE4OSwyNDgsMC4wNSkiIHN0cm9rZS13aWR0aD0iMSIgb3BhY2l0eT0iMC40Ii8+PHBhdGggZD0iTTI1MCwxMDAgUTIyMCwxMzAgMjYwLDE3MCBRMjgwLDIwMCAyNTAsMjMwIiBzdHJva2U9InJnYmEoMjUzLDIyNCwxMTUsMC4wNCkiIHN0cm9rZS13aWR0aD0iMS4yIiBvcGFjaXR5PSIwLjMiLz48L2c+PC9zdmc+`

// Параллакс
const mousePosition = reactive({ x: 0, y: 0 })
const mouseIntensity = ref(0)
const cloud1 = reactive({ x: 0, y: 0 })
const cloud2 = reactive({ x: 0, y: 0 })

const initClouds = () => {
  cloud1.x = window.innerWidth / 2 - 192
  cloud1.y = window.innerHeight / 3
  cloud2.x = window.innerWidth / 1.6 - 160
  cloud2.y = window.innerHeight / 1.5
}

onMounted(async () => {
  initClouds()
  window.addEventListener('resize', initClouds)
  await loadProjects()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', initClouds)
})

const handleMouseMove = (e) => {
  mousePosition.x = e.clientX
  mousePosition.y = e.clientY
  mouseIntensity.value = Math.min(1, Math.sqrt(
    Math.pow(e.clientX - window.innerWidth / 2, 2) +
    Math.pow(e.clientY - window.innerHeight / 2, 2)
  ) / Math.max(window.innerWidth, window.innerHeight) * 2)

  const speed1 = 0.03
  const speed2 = 0.02
  cloud1.x = window.innerWidth / 2 - 192 + (window.innerWidth / 2 - e.clientX) * speed1
  cloud1.y = window.innerHeight / 3 + (window.innerHeight / 2 - e.clientY) * speed1
  cloud2.x = window.innerWidth / 1.6 - 160 + (window.innerWidth / 2 - e.clientX) * speed2
  cloud2.y = window.innerHeight / 1.5 + (window.innerHeight / 2 - e.clientY) * speed2
}

const handleMouseLeave = () => {
  mouseIntensity.value = 0
}

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

const deleteProject = async (id) => {
  const confirmed = await confirm(
    'Удалить проект?',
    'Все сцены и данные будут безвозвратно удалены.'
  )
  if (!confirmed) return
  try {
    await apiDeleteProject(id)
    showSuccess('Проект удалён')
    await loadProjects()
  } catch (err) {
    showError('Ошибка удаления: ' + err.message)
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
.project-item {
  animation: fade-in-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(10px);
}

/* Van Gogh спиннер */
.loading-spinner {
  width: 40px;
  height: 40px;
  position: relative;
}
.loading-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
  background: conic-gradient(
    transparent,
    #fde047 25%,
    #a78bfa 60%,
    transparent 85%
  );
  -webkit-mask: radial-gradient(farthest-side, transparent 85%, #000 85%);
}

@keyframes fade-in { to { opacity: 1; } }
@keyframes fade-in-up { to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
</style>