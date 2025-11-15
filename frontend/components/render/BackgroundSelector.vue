<template>
  <div class="bg-slate-800/40 backdrop-blur-sm rounded-xl p-5 border border-slate-700/50 fade-in-up" style="animation-delay: 0.1s">
    <h3 class="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <circle cx="15.5" cy="8.5" r="1.5" />
        <circle cx="8.5" cy="15.5" r="1.5" />
        <circle cx="15.5" cy="15.5" r="1.5" />
        <line x1="3" y1="12" x2="21" y2="12" />
        <line x1="12" y1="3" x2="12" y2="21" />
      </svg>
      Выберите фон
    </h3>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div 
        v-for="bg in backgrounds" 
        :key="bg.value"
        class="bg-slate-800/30 rounded-xl p-4 border-2 cursor-pointer transition-all duration-300 hover:border-yellow-400/50 transform hover:scale-[1.02] fade-in"
        :class="{ 
          'border-yellow-400/80 bg-slate-800/50': modelValue === bg.value,
          'opacity-50 cursor-not-allowed': disabled,
          'animate-fade-in': true
        }"
        :style="{ animationDelay: `${backgrounds.findIndex(b => b.value === bg.value) * 0.05}s` }"
        @click="!disabled && $emit('update:modelValue', bg.value)"
      >
        <div class="relative w-full h-24 mb-3 bg-slate-900/50 rounded-lg overflow-hidden">
          <div 
            v-if="bg.value === 'minecraft'" 
            class="absolute inset-0 animate-minecraft-bg"
          ></div>
          <div 
            v-else-if="bg.value === 'subway'" 
            class="absolute inset-0 animate-subway-bg"
          ></div>
          <div 
            v-else-if="bg.value === 'abstract'" 
            class="absolute inset-0 animate-abstract-bg"
          ></div>
        </div>
        <h4 class="font-semibold text-slate-200 text-sm mb-1">{{ bg.name }}</h4>
        <p class="text-slate-500 text-xs">{{ bg.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: 'minecraft' },
  disabled: { type: Boolean, default: false }
})

defineEmits(['update:modelValue'])

const backgrounds = [
  {
    value: 'minecraft',
    name: 'Minecraft Паркур',
    description: 'Классический брейнрот фон'
  },
  {
    value: 'subway',
    name: 'Subway Surfers',
    description: 'Динамический раннер'
  },
  {
    value: 'abstract',
    name: 'Абстрактные пятна',
    description: 'Минималистичный стиль'
  }
]
</script>

<style scoped>
/* Анимации из основной страницы */
@keyframes minecraftPulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
.animate-minecraft-bg {
  background: 
    linear-gradient(90deg, 
      rgba(253, 224, 71, 0.15) 25%, 
      transparent 25%,
      transparent 50%,
      rgba(253, 224, 71, 0.15) 50%,
      rgba(253, 224, 71, 0.15) 75%,
      transparent 75%
    ),
    linear-gradient(rgba(253, 224, 71, 0.05) 25%, transparent 25%);
  background-size: 20px 20px;
  animation: minecraftPulse 2s infinite;
}

@keyframes subwayMove {
  0% { background-position: 0 0; }
  100% { background-position: 40px 0; }
}
.animate-subway-bg {
  background: 
    linear-gradient(90deg, 
      transparent 40%, 
      rgba(196, 181, 253, 0.15) 45%, 
      rgba(196, 181, 253, 0.15) 55%, 
      transparent 60%
    );
  background-size: 40px 100%;
  animation: subwayMove 1.5s linear infinite;
}

@keyframes abstractFloat {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(2px, -2px); }
  50% { transform: translate(-2px, 2px); }
  75% { transform: translate(2px, 2px); }
}
.animate-abstract-bg {
  background: 
    radial-gradient(circle at 20% 30%, rgba(103, 232, 249, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(103, 232, 249, 0.08) 0%, transparent 60%),
    radial-gradient(circle at 50% 20%, rgba(103, 232, 249, 0.07) 0%, transparent 55%);
  animation: abstractFloat 4s ease-in-out infinite;
}

.fade-in {
  animation: fade-in 0.5s ease-out forwards;
  opacity: 0;
}
@keyframes fade-in {
  to { opacity: 1; }
}
</style>