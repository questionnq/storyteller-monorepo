<template>
  <div class="card bg-base-200 shadow-xl hover:shadow-2xl transition-all hover:scale-[1.02]">
    <div class="card-body">
      <h3 class="card-title text-lg">{{ project.title }}</h3>
      <p class="text-sm opacity-70 line-clamp-2">{{ project.description }}</p>
      
      <div class="flex justify-between items-center mt-4">
        <span class="text-xs opacity-50">
          {{ formatDate(project.created_at) }}
        </span>
        <div class="flex gap-2">
          <button 
            class="btn btn-primary btn-sm"
            @click="openProject"
            :disabled="isLoading"
          >
            Открыть
          </button>
          <button 
            class="btn btn-ghost btn-sm"
            @click="emit('delete', project.id)"
            :disabled="isLoading"
          >
            <span class="text-error">✕</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  project: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click', 'delete'])

const router = useRouter()

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const openProject = () => {
  router.push(`/project/${props.project.id}`)
}
</script>