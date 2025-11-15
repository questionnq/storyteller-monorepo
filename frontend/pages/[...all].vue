<template>
  <div 
    class="min-h-screen relative overflow-hidden"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- Фон -->
    <div class="absolute inset-0 bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950"></div>
    
    <!-- Динамические звёзды вместо мазков -->
    <div class="absolute inset-0 overflow-hidden">
      <div 
        v-for="star in dynamicStars" 
        :key="star.id"
        class="dynamic-star"
        :style="getStarStyle(star)"
      ></div>
    </div>

    <!-- Завихрения -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="swirl-cloud swirl-1"></div>
      <div class="swirl-cloud swirl-2"></div>
      <div class="swirl-cloud swirl-3"></div>
    </div>

    <!-- Фрагменты сценария -->
    <div class="absolute inset-0 overflow-visible pointer-events-none">
      <div 
        v-for="(fragment, i) in scriptFragments" 
        :key="i"
        class="script-fragment"
        :style="getFragmentStyle(fragment)"
      >
        {{ fragment.text }}
      </div>
    </div>

    <!-- Свечение под курсором -->
    <div 
      class="absolute inset-0 opacity-25"
      :style="{
        background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(253, 224, 71, 0.15) 0%, transparent 60%)`
      }"
    ></div>

    <!-- Контент -->
    <div class="relative z-10 flex flex-col justify-center min-h-screen px-4">
      <div class="max-w-md mx-auto text-center">
        <!-- Анимированный 404 -->
        <div 
          class="relative inline-flex items-center justify-center w-32 h-32 rounded-3xl mb-8 mx-auto cursor-pointer"
          @click="handle404Click"
        >
          <div 
            class="absolute inset-0 bg-gradient-to-br from-yellow-400/40 to-blue-500/40 backdrop-blur-sm rounded-3xl border border-yellow-400/50"
            :style="{
              transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
              boxShadow: `0 0 30px rgba(253, 224, 71, ${glowIntensity})`
            }"
          ></div>
          <span 
            class="text-6xl font-bold text-yellow-300 drop-shadow-[0_0_16px_rgba(253,224,71,0.7)] transition-all duration-300"
            :style="{ transform: `scale(${scale404})` }"
          >
            404
          </span>
        </div>

        <h1 class="text-4xl md:text-5xl font-bold mb-6">
          <span class="text-yellow-300">Страница<br /></span>
          <span class="text-slate-100">затерялась в истории...</span>
        </h1>

        <p class="text-slate-200 mb-10 leading-relaxed">
          Похоже, вы забрели в уголок Storyteller AI, где даже ИИ делает перерыв на кофе.<br />
          Но не волнуйтесь — ваши проекты ждут вас дома. Или, может, пора создать что-то новое?
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink 
            to="/"
            class="btn btn-van-gogh-primary btn-lg rounded-full group"
          >
            <span class="group-hover:animate-pulse">Вернуться на главную</span>
          </NuxtLink>
          <NuxtLink 
            to="/dashboard"
            class="btn btn-van-gogh-outline btn-lg rounded-full group"
          >
            <span class="group-hover:animate-pulse">Мои проекты</span>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'

const mousePosition = reactive({ x: 0, y: 0 })
const rotateX = ref(0)
const rotateY = ref(0)
const scale404 = ref(1)
const glowIntensity = ref(0.5)

// Звёзды
const dynamicStars = ref([])

// Фрагменты сценария
const scriptFragments = ref([
  { text: 'Интересные факты про электроовец', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Этот мужчина...', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Знаете ли вы, что...', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Я мопс, мне...?', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Он выжил... но не ожидал этого', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Никто не верил, пока...', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Это изменило всё за 3 секунды', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Она сказала "да"... но не ему', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Через час его не стало...', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'А потом раздался крик', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Он не знал, что это — ловушка', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Её секрет шокировал всех', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Это было не то, чем казалось', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Он проснулся... в другом теле', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'Они думали, что всё кончено...', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 },
  { text: 'А ведь началось всё с мелочи', x: 0, y: 0, opacity: 0, speed: 0.01, offsetX: 0, offsetY: 0 }
])

// Безопасные геттеры стилей
const getStarStyle = (star) => {
  return {
    left: `${star.x}%`,
    top: `${star.y}%`,
    width: `${star.size}px`,
    height: `${star.size}px`,
    opacity: star.opacity,
    transform: `translate(${star.offsetX}px, ${star.offsetY}px)`,
    animationDelay: `${star.delay}s`,
    background: star.color,
    boxShadow: star.glow
  }
}

const getFragmentStyle = (fragment) => {
  return {
    opacity: fragment.opacity,
    left: `${fragment.x}%`,
    top: `${fragment.y}%`,
    transform: `translate(${fragment.offsetX}px, ${fragment.offsetY}px)`
  }
}

// Генерация звёзд
const generateStars = () => {
  const stars = []
  const colors = [
    { color: '#fde047', glow: '0 0 8px #fde047, 0 0 16px rgba(253,224,71,0.3)' },
    { color: '#c4b5fd', glow: '0 0 8px #c4b5fd, 0 0 16px rgba(196,181,253,0.3)' },
    { color: '#67e8f9', glow: '0 0 8px #67e8f9, 0 0 16px rgba(103,232,249,0.3)' }
  ]
  
  for (let i = 0; i < 100; i++) {
    const colorSet = colors[i % colors.length]
    stars.push({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2.5 + 0.8,
      opacity: 0.4 + Math.random() * 0.6,
      color: colorSet.color,
      glow: colorSet.glow,
      speed: 0.015 + Math.random() * 0.025,
      depth: Math.random(),
      offsetX: 0,
      offsetY: 0,
      delay: Math.random() * 4
    })
  }
  return stars
}

// Расчёт безопасных координат для фрагментов
const calculateFragmentPositions = () => {
  return scriptFragments.value.map((frag, i) => {
    // Левая и правая зоны
    const isLeft = i % 2 === 0
    const x = isLeft ? (5 + Math.random() * 20) : (75 + Math.random() * 20)
    const y = 10 + Math.random() * 80
    
    return {
      ...frag,
      x,
      y,
      opacity: 0.5 + Math.random() * 0.3,
      speed: 0.01 + Math.random() * 0.015
    }
  })
}

onMounted(() => {
  dynamicStars.value = generateStars()
  scriptFragments.value = calculateFragmentPositions()
  
  // Постепенное появление фрагментов
  setTimeout(() => {
    scriptFragments.value.forEach(frag => {
      frag.opacity = 0.5 + Math.random() * 0.3
    })
  }, 300)
})

const handleMouseMove = (e) => {
  mousePosition.x = e.clientX
  mousePosition.y = e.clientY

  // Параллакс для звёзд
  dynamicStars.value.forEach(star => {
    const depthFactor = 1 - star.depth * 0.7
    star.offsetX = (e.clientX - window.innerWidth / 2) * star.speed * depthFactor
    star.offsetY = (e.clientY - window.innerHeight / 2) * star.speed * depthFactor
  })

  // Параллакс для фрагментов
  scriptFragments.value.forEach(frag => {
    frag.offsetX = (e.clientX - window.innerWidth / 2) * frag.speed
    frag.offsetY = (e.clientY - window.innerHeight / 2) * frag.speed
  })

  // 3D-эффект для 404
  const rect = e.currentTarget.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  rotateY.value = ((e.clientX - centerX) / rect.width) * 10
  rotateX.value = ((centerY - e.clientY) / rect.height) * 10
  scale404.value = 1.05
  glowIntensity.value = 0.8
}

const handleMouseLeave = () => {
  rotateX.value = 0
  rotateY.value = 0
  scale404.value = 1
  glowIntensity.value = 0.5
  
  dynamicStars.value.forEach(star => {
    star.offsetX = 0
    star.offsetY = 0
  })
  
  scriptFragments.value.forEach(frag => {
    frag.offsetX = 0
    frag.offsetY = 0
  })
}

const handle404Click = () => {
  scale404.value = 1.2
  glowIntensity.value = 1
  setTimeout(() => {
    scale404.value = 1
    glowIntensity.value = 0.5
  }, 300)
}
</script>

<style scoped>
.swirl-cloud {
  position: absolute;
  width: 200px;
  height: 100px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(253, 224, 71, 0.1) 0%, transparent 70%);
  animation: swirl 20s linear infinite;
  filter: blur(1px);
}

.swirl-1 { top: 10%; left: 5%; animation-duration: 25s; }
.swirl-2 { bottom: 15%; right: 10%; animation-duration: 30s; animation-direction: reverse; }
.swirl-3 { top: 40%; right: 20%; animation-duration: 35s; }

.dynamic-star {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  transition: transform 0.1s ease-out;
}

.script-fragment {
  position: absolute;
  color: rgba(253, 224, 71, 0.8);
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  max-width: 140px;
  word-wrap: break-word;
  text-align: center;
  pointer-events: none;
  text-shadow: 0 0 8px rgba(253, 224, 71, 0.8);
  transition: transform 0.1s ease-out, opacity 0.5s ease;
}

@keyframes swirl {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.1); }
  100% { transform: rotate(360deg) scale(1); }
}

@media (max-width: 640px) {
  .script-fragment { font-size: 0.65rem; max-width: 110px; }
}
</style>