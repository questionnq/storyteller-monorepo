<template>
  <div class="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50 relative group">
    <!-- Шапка сцены -->
    <div class="flex justify-between items-start mb-5">
      <!-- Номер сцены -->
      <div class="flex items-center gap-3">
        <div class="bg-gradient-to-br from-yellow-400 to-blue-500 text-white rounded-2xl w-12 h-12 flex items-center justify-center font-bold text-lg shadow-sm">
          {{ scene.scene_number }}
        </div>
        <div>
          <h3 class="font-bold text-slate-100 text-lg">Сцена {{ scene.scene_number }}</h3>
          <div class="flex items-center gap-1.5 mt-0.5">
            <svg 
              v-if="isSaving" 
              width="14" 
              height="14" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2"
              class="text-yellow-400 animate-pulse"
            >
              <path d="M12 2v4m0 0l-3-3m3 3l3-3" />
              <circle cx="12" cy="12" r="9" />
            </svg>
            <svg 
              v-else-if="lastSaved" 
              width="14" 
              height="14" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2"
              class="text-green-400"
            >
              <path d="M9 12l2 2 4-4" />
            </svg>
            <span 
              v-if="isSaving" 
              class="text-xs text-yellow-300"
            >
              Сохранение...
            </span>
            <span 
              v-else-if="lastSaved" 
              class="text-xs text-green-400"
            >
              Сохранено {{ lastSaved }}
            </span>
          </div>
        </div>
      </div>

      <!-- Кнопка удаления -->
      <button 
        class="btn btn-ghost btn-sm btn-circle opacity-0 group-hover:opacity-100 transition-opacity"
        @click="$emit('delete', scene.id)"
        aria-label="Удалить сцену"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Описание действия -->
    <div class="mb-5">
      <label class="flex items-center gap-2.5 mb-2.5">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-yellow-400/90">
          <polygon points="7,21 7,10 12,6 17,10 17,21" />
          <path d="M12,18L12,6" />
        </svg>
        <span class="font-bold text-slate-200">Описание действия</span>
      </label>
      <textarea 
        v-model="localScene.action"
        class="w-full min-h-[100px] text-sm bg-slate-800/50 border border-slate-700/50 rounded-xl px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400/30 transition-colors"
        placeholder="Что происходит на экране?"
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- Диалоги -->
    <div class="mb-5">
      <label class="flex items-center gap-2.5 mb-2.5">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-blue-400/90">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        <span class="font-bold text-slate-200">Диалоги персонажей</span>
      </label>
      <textarea 
        v-model="localScene.dialogue"
        class="w-full min-h-[60px] text-sm bg-slate-800/50 border border-slate-700/50 rounded-xl px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400/30 transition-colors"
        placeholder="Реплики персонажей..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- Текст за кадром -->
    <div class="mb-5">
      <label class="flex items-center gap-2.5 mb-2.5">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-purple-400/90">
          <path d="M17 14v6m-3-3h6M6.26 9.7a9 9 0 0 1 11.48 0M6.26 18.7a9 9 0 0 0 11.48 0" />
          <circle cx="12" cy="5" r="4" />
        </svg>
        <span class="font-bold text-slate-200">Текст за кадром (Voiceover)</span>
      </label>
      <textarea 
        v-model="localScene.voice_over"
        class="w-full min-h-[80px] text-sm font-mono bg-slate-800/50 border border-slate-700/50 rounded-xl px-3 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400/30 transition-colors"
        placeholder="Текст для озвучки..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- Визуальный промпт -->
    <div class="mb-5">
      <label class="flex items-center gap-2.5 mb-2.5">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-emerald-400/90">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <path d="M21 15l-1.5-1.5" />
          <path d="M15.5 15.5l-1.5-1.5" />
          <path d="M10 15l-1.5-1.5" />
        </svg>
        <span class="font-bold text-slate-200">Визуальный промпт</span>
      </label>
      <textarea 
        v-model="localScene.visual_prompt"
        class="w-full min-h-[60px] text-xs bg-slate-800/50 border border-slate-700/50 rounded-xl px-3 py-2 text-slate-300 placeholder-slate-600 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400/30 transition-colors opacity-90"
        placeholder="Описание кадра для ИИ-художника (на английском)..."
        @input="debounceSave"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  scene: {
    type: Object,
    required: true
  },
  isGeneratingImage: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update', 'delete', 'regenerate-image'])

const localScene = ref({ 
  id: props.scene.id,
  scene_number: props.scene.scene_number || 1,
  action: props.scene.action || '',
  dialogue: props.scene.dialogue || '',
  voice_over: props.scene.voice_over || '',
  visual_prompt: props.scene.visual_prompt || ''
})

const isSaving = ref(false)
const lastSaved = ref('')
let saveTimeout = null

watch(() => props.scene, (newVal) => {
  localScene.value = { 
    id: newVal.id,
    scene_number: newVal.scene_number || 1,
    action: newVal.action || '',
    dialogue: newVal.dialogue || '',
    voice_over: newVal.voice_over || '',
    visual_prompt: newVal.visual_prompt || ''
  }
}, { deep: true })

const debounceSave = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  isSaving.value = true
  saveTimeout = setTimeout(() => {
    saveChanges()
  }, 800)
}

const saveChanges = () => {
  emit('update', {
    id: localScene.value.id,
    scene_number: localScene.value.scene_number,
    action: localScene.value.action,
    dialogue: localScene.value.dialogue,
    voice_over: localScene.value.voice_over,
    visual_prompt: localScene.value.visual_prompt
  })
  
  isSaving.value = false
  lastSaved.value = new Date().toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
  
  setTimeout(() => {
    lastSaved.value = ''
  }, 3000)
}
</script>