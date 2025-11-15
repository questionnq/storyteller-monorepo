<template>
  <div 
    class="hero min-h-screen relative overflow-hidden"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <div class="absolute inset-0 bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950"></div>
    
    <div class="van-gogh-texture"></div>

    <div 
      class="absolute inset-0 opacity-25 pointer-events-none"
      :style="{
        background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(253, 224, 71, 0.2) 0%, transparent 60%)`
      }"
    ></div>

    <div class="absolute inset-0 overflow-hidden">
      <div v-for="i in 80" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <div class="absolute inset-0 overflow-hidden">
      <div class="swirl-cloud swirl-1"></div>
      <div class="swirl-cloud swirl-2"></div>
      <div class="swirl-cloud swirl-3"></div>
      <div class="swirl-cloud swirl-4" style="top: 60%; left: 30%; animation-duration: 40s;"></div>
    </div>

    <div class="hero-content text-center relative z-10">
      <div 
        class="max-w-md bg-gradient-to-br from-amber-400/10 to-blue-500/15 backdrop-blur-xl rounded-3xl p-8 border border-yellow-400/30 card-glow"
        :style="cardStyle"
      >
        <h1 class="text-5xl font-bold mb-6">
          <span class="text-yellow-200 drop-shadow-[0_0_8px_rgba(253,224,71,0.4)]">Storyteller</span>
          <span class="text-slate-100">AI</span>
        </h1>
        <p class="py-6 text-slate-200 leading-relaxed">
          Генерируй сториборды и короткие видеоролики за минуты с помощью ИИ
        </p>
        
        <div class="flex gap-4 justify-center flex-col sm:flex-row">
          <NuxtLink 
            to="/dashboard" 
            class="btn btn-van-gogh-primary btn-lg rounded-full group relative"
          >
            <span class="relative z-10 group-hover:animate-pulse">Начать работу</span>
          </NuxtLink>
          <NuxtLink 
            v-if="!user" 
            to="/login" 
            class="btn btn-van-gogh-outline btn-lg rounded-full group relative"
          >
            <span class="relative z-10 group-hover:animate-pulse">Войти</span>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { user } = useSupabaseAuth()

definePageMeta({
  layout: 'default'
})

const mousePosition = reactive({ x: 0, y: 0 })
const cardOffset = reactive({ x: 0, y: 0 })

function handleMouseMove(e) {
  mousePosition.x = e.clientX
  mousePosition.y = e.clientY

  const rect = e.currentTarget.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  cardOffset.x = (e.clientX - centerX) / 60
  cardOffset.y = (e.clientY - centerY) / 60
}

function handleMouseLeave() {
  cardOffset.x = 0
  cardOffset.y = 0
}

const cardStyle = computed(() => ({
  transform: `translate(${cardOffset.x}px, ${cardOffset.y}px) rotateX(${cardOffset.y * 0.6}deg) rotateY(${cardOffset.x * 0.6}deg)`,
  transition: 'transform 0.1s ease-out'
}))

function getStarStyle(index) {
  const size = Math.random() * 2.5 + 0.8
  const left = Math.random() * 100
  const top = Math.random() * 100
  const animationDelay = Math.random() * 4
  const opacity = 0.4 + Math.random() * 0.6
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${animationDelay}s`,
    opacity: opacity
  }
}
</script>

<style scoped>
@keyframes twinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

@keyframes swirl {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.05); }
  100% { transform: rotate(360deg) scale(1); }
}
</style>