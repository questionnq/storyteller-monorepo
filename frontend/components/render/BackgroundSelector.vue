<template>
  <div class="bg-base-200 rounded-lg p-4 shadow-lg">
    <h3 class="text-lg font-bold mb-4">Шаг 2: Выберите фон</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div 
        v-for="bg in backgrounds" 
        :key="bg.value"
        class="card cursor-pointer hover:shadow-xl transition-all"
        :class="{ 'ring-2 ring-primary': modelValue === bg.value }"
        @click="$emit('update:modelValue', bg.value)"
      >
        <figure class="px-4 pt-4">
          <div class="bg-base-300 w-full h-32 rounded-lg flex items-center justify-center text-4xl">
            {{ bg.emoji }}
          </div>
        </figure>
        <div class="card-body p-4">
          <h4 class="card-title text-sm">{{ bg.name }}</h4>
          <p class="text-xs opacity-70">{{ bg.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: 'minecraft' }
})

defineEmits(['update:modelValue'])

const backgrounds = [
  {
    value: 'minecraft',
    name: 'Minecraft Паркур',
    description: 'Классический брейнрот фон',
    emoji: '🎮'
  },
  {
    value: 'subway',
    name: 'Subway Surfers',
    description: 'Динамический раннер',
    emoji: '🏃'
  },
  {
    value: 'abstract',
    name: 'Абстрактные пятна',
    description: 'Минималистичный стиль',
    emoji: '🎨'
  }
]
</script>