<!-- components/ProjectCard.vue -->
<template>
  <div 
    class="card project-card rounded-2xl p-5 border border-yellow-400/20 bg-gradient-to-br from-slate-800/30 to-slate-900/50 backdrop-blur-sm transition-all duration-300 ease-out"
    @click="openProject"
  >
    <div class="flex flex-col h-full">
      <h3 class="font-bold text-slate-100 mb-2 line-clamp-1">{{ project.title }}</h3>
      <p class="text-slate-300 text-sm mb-4 flex-grow line-clamp-2">
        {{ project.description || 'Без описания' }}
      </p>
      
      <div class="mt-auto flex justify-between items-center pt-3 border-t border-slate-700/40">
        <span class="text-xs text-slate-400">
          {{ formatDate(project.created_at) }}
        </span>
        <div class="flex gap-2">
          <button 
            class="btn btn-sm px-3 py-1.5 text-xs font-medium bg-yellow-400/10 hover:bg-yellow-400/20 text-yellow-200 border border-yellow-400/30 rounded-lg transition-colors"
            @click.stop="openProject"
            :disabled="isLoading"
          >
            Открыть
          </button>
          <button 
            class="btn btn-sm px-3 py-1.5 text-xs font-medium bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 rounded-lg transition-colors"
            @click.stop="emit('delete', project.id)"
            :disabled="isLoading"
          >
            Удалить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  project: { type: Object, required: true },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['click', 'delete'])
const router = useRouter()

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const openProject = () => {
  router.push(`/project/${props.project.id}`)
}
</script>

<style scoped>
.project-card {
  cursor: pointer;
}
.project-card:hover {
  border-color: rgba(253, 224, 71, 0.4);
  box-shadow: 0 8px 20px -8px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(253, 224, 71, 0.15);
}
</style>