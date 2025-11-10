<template>
  <div class="bg-base-200 rounded-xl p-6 shadow-lg border-l-4 border-primary">
    <div class="flex justify-between items-start mb-4">
      <div class="flex items-center gap-3">
        <div class="bg-primary text-primary-content rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg">
          {{ scene.scene_number }}
        </div>
        <div>
          <h3 class="font-bold text-lg">Сцена {{ scene.scene_number }}</h3>
        </div>
      </div>
      <button class="btn btn-ghost btn-sm btn-circle" @click="$emit('delete')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- БЛОК: Описание действия -->
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎬</span>
        <label class="label-text font-bold text-base">Описание действия</label>
      </div>
      <textarea 
        v-model="localScene.action"
        class="textarea textarea-bordered w-full min-h-[100px] text-sm"
        placeholder="Что происходит на экране? Подробно опишите действия, выражения, движения..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- БЛОК: Диалоги -->
    <div class="mb-5" v-if="localScene.dialogue !== undefined">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">💬</span>
        <label class="label-text font-bold text-base">Диалоги персонажей</label>
      </div>
      <textarea 
        v-model="localScene.dialogue"
        class="textarea textarea-bordered w-full min-h-[60px] text-sm"
        placeholder="Реплики персонажей..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- БЛОК: Текст за кадром (VOICEOVER) -->
    <div class="mb-5" v-if="localScene.voice_over !== undefined">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎙️</span>
        <label class="label-text font-bold text-base">Текст за кадром (Voiceover)</label>
      </div>
      <textarea 
        v-model="localScene.voice_over"
        class="textarea textarea-bordered w-full min-h-[80px] text-sm font-mono bg-base-300"
        placeholder="Текст, который будет озвучен поверх видео..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- БЛОК: Визуальный промпт -->
    <div class="mb-5" v-if="localScene.visual_prompt !== undefined">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎨</span>
        <label class="label-text font-bold text-base">Визуальный промпт</label>
      </div>
      <textarea 
        v-model="localScene.visual_prompt"
        class="textarea textarea-bordered w-full min-h-[60px] text-xs opacity-80"
        placeholder="Детальное описание кадра для ИИ-художника (150-200 символов, на английском)..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- БЛОК для уточняющего промпта при перегенерации -->
    <div class="mb-5" v-if="showStylePrompt">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">✨</span>
        <label class="label-text font-bold text-base">Уточнить стиль</label>
      </div>
      <input 
        v-model="stylePrompt"
        class="input input-bordered w-full text-sm"
        placeholder="Например: в стиле пиксель-арт"
      />
    </div>

    <!-- КНОПКИ ДЕЙСТВИЙ -->
    <div class="flex gap-2 mt-6 pt-4 border-t border-base-300">
      <button 
        class="btn btn-primary flex-1 btn-sm" 
        @click="toggleStylePrompt"
        v-if="!showStylePrompt"
      >
        ✨ Уточнить стиль
      </button>
      <button 
        class="btn btn-primary flex-1 btn-sm" 
        @click="regenerateImage"
        :disabled="props.isGeneratingImage"
      >
        <span class="loading loading-spinner" v-if="props.isGeneratingImage"></span>
        {{ props.isGeneratingImage ? 'Генерация...' : '🎨 Перегенерить картинку' }}
      </button>
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
  scene_number: props.scene.scene_number || 1,
  action: props.scene.action || '',
  dialogue: props.scene.dialogue || '',
  voice_over: props.scene.voice_over || '',
  visual_prompt: props.scene.visual_prompt || '',
  ...props.scene 
})

const showStylePrompt = ref(false)
const stylePrompt = ref('')
let saveTimeout = null

watch(() => props.scene, (newVal) => {
  localScene.value = { 
    scene_number: newVal.scene_number || 1,
    action: newVal.action || '',
    dialogue: newVal.dialogue || '',
    voice_over: newVal.voice_over || '',
    visual_prompt: newVal.visual_prompt || '',
    ...newVal 
  }
}, { deep: true })

const debounceSave = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  saveTimeout = setTimeout(() => {
    saveChanges()
  }, 500)
}

const saveChanges = () => {
  emit('update', localScene.value)
}

const toggleStylePrompt = () => {
  showStylePrompt.value = !showStylePrompt.value
}

const regenerateImage = () => {
  emit('regenerate-image', {
    sceneNumber: localScene.value.scene_number,
    style: stylePrompt.value || 'cinematic'
  })
  
  // Сбросить поле уточнения после использования
  if (stylePrompt.value) {
    stylePrompt.value = ''
    showStylePrompt.value = false
  }
}
</script>