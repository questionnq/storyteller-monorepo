<template>
  <div 
    class="min-h-screen relative overflow-hidden"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- Фон -->
    <div class="absolute inset-0 bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950"></div>
    
    <!-- Текстура мазков (base layer) -->
    <div 
      class="absolute inset-0 opacity-8"
      style="background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMDAgMzAwIj48ZyBmaWxsPSJub25lIj48cGF0aCBkPSJNNDAsODAgUTcwLDQwIDEyMCw3MCBRMTYwLDkwIDE5MCw2MCIgc3Ryb2tlPSJyZ2JhKDI1MywyMjQsMTE1LDAuMDgpIiBzdHJva2Utd2lkdGg9IjIiIG9wYWNpdHk9IjAuNiIvPjxwYXRoIGQ9Ik0yMCwxNTAgUTYwLDEyMCAxMDAsMTYwIFEyMDAsMTgwIDE4MCwxNDAiIHN0cm9rZT0icmdiYSgxMzksOTIsMjQ2LDAuMDYpIiBzdHJva2Utd2lkdGg9IjEuNSIgb3BhY2l0eT0iMC41Ii8+PHBhdGggZD0iTTYwLDIyMCBRMTAwLDIwMCAxNDAsMjMwIFE1MCwyNTAgMjIwLDIyMCIgc3Ryb2tlPSJyZ2JhKDU2LDE4OSwyNDgsMC4wNSkiIHN0cm9rZS13aWR0aD0iMSIgb3BhY2l0eT0iMC40Ii8+PHBhdGggZD0iTTI1MCwxMDAgUTIyMCwxMzAgMjYwLDE3MCBRMjgwLDIwMCAyNTAsMjMwIiBzdHJva2U9InJnYmEoMjUzLDIyNCwxMTUsMC4wNCkiIHN0cm9rZS13aWR0aD0iMS4yIiBvcGFjaXR5PSIwLjMiLz48L2c+PC9zdmc+'); background-size: 300px 300px;"
    ></div>

    <!-- Завихрения (медленные) -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="swirl swirl-1"></div>
      <div class="swirl swirl-2"></div>
      <div class="swirl swirl-3"></div>
    </div>

    <!-- Параллакс-звёзды (foreground) -->
    <div class="absolute inset-0 overflow-hidden">
      <div 
        v-for="star in parallaxStars" 
        :key="star.id"
        class="parallax-star"
        :style="{
          left: `${star.x}%`,
          top: `${star.y}%`,
          transform: `translate(${star.offsetX}px, ${star.offsetY}px)`,
          opacity: star.opacity,
          width: `${star.size}px`,
          height: `${star.size}px`
        }"
      ></div>
    </div>

    <!-- Фрагменты сценария -->
    <div class="absolute inset-0 overflow-visible pointer-events-none">
      <div 
        v-for="(fragment, i) in scriptFragments" 
        :key="i"
        class="script-fragment"
        :class="{
          'animate-fade-in': fragment.initial,
          'animate-slide-in': !fragment.initial
        }"
        :style="{
          left: `${fragment.x}%`,
          top: `${fragment.y}%`,
          transform: `translate(${fragment.offsetX}px, ${fragment.offsetY}px)`,
          opacity: fragment.opacity,
          '--delay': `${fragment.delay}s`
        }"
      >
        {{ fragment.text }}
      </div>
    </div>

    <!-- Свечение под курсором -->
    <div 
      class="absolute inset-0 opacity-30"
      :style="{
        background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(253, 224, 71, 0.2) 0%, transparent 60%)`
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
            class="btn btn-van-gogh-primary btn-lg rounded-full transform hover:scale-105 transition-all duration-300 group"
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
import { onMounted, ref, reactive, computed } from 'vue'

const mousePosition = reactive({ x: 0, y: 0 })
const rotateX = ref(0)
const rotateY = ref(0)
const scale404 = ref(1)
const glowIntensity = ref(0.5)
const contentRect = ref({ width: 0, height: 0 })

// Параллакс-звёзды
const parallaxStars = ref([])

// Фрагменты сценария (только тексты)
const scriptFragmentTexts = [
  'Интересные факты про электроовец',
  'Этот мужчина...',
  'Знаете ли вы, что...',
  'Я мопс, мне...?',
  'Он выжил... но не ожидал этого',
  'Никто не верил, пока...',
  'Это изменило всё за 3 секунды',
  'Она сказала "да"... но не ему',
  'Через час его не стало...',
  'А потом раздался крик',
  'Он не знал, что это — ловушка',
  'Её секрет шокировал всех',
  'Это было не то, чем казалось',
  'Он проснулся... в другом теле',
  'Они думали, что всё кончено...',
  'А ведь началось всё с мелочи'
]

// Динамические фрагменты с позициями
const scriptFragments = ref([])

// Области для размещения фрагментов (в процентах)
const safeZone = computed(() => {
  const padding = 15 // отступ от центрального контента в процентах
  const contentWidth = Math.min(80, 100 - padding * 2) // максимальная ширина контента
  const contentHeight = 60 // высота контента в процентах
  
  return {
    left: (100 - contentWidth) / 2,
    right: (100 + contentWidth) / 2,
    top: (100 - contentHeight) / 2,
    bottom: (100 + contentHeight) / 2
  }
})

const generateFragmentPositions = () => {
  const regions = [
    // Верхняя полоса (над контентом)
    { 
      x: [safeZone.value.left - 10, safeZone.value.right + 10], 
      y: [5, safeZone.value.top - 5],
      speedRange: [0.01, 0.015]
    },
    // Нижняя полоса (под контентом)
    { 
      x: [safeZone.value.left - 10, safeZone.value.right + 10], 
      y: [safeZone.value.bottom + 5, 95],
      speedRange: [0.012, 0.018]
    },
    // Левая полоса
    { 
      x: [5, safeZone.value.left - 5], 
      y: [safeZone.value.top - 10, safeZone.value.bottom + 10],
      speedRange: [0.015, 0.02]
    },
    // Правая полоса
    { 
      x: [safeZone.value.right + 5, 95], 
      y: [safeZone.value.top - 10, safeZone.value.bottom + 10],
      speedRange: [0.014, 0.022]
    }
  ]

  return scriptFragmentTexts.map((text, index) => {
    const region = regions[index % regions.length]
    const xRange = region.x
    const yRange = region.y
    
    // Генерируем позицию в пределах региона
    const x = xRange[0] + Math.random() * (xRange[1] - xRange[0])
    const y = yRange[0] + Math.random() * (yRange[1] - yRange[0])
    
    // Генерируем скорость в пределах диапазона региона
    const minSpeed = region.speedRange[0]
    const maxSpeed = region.speedRange[1]
    const speed = minSpeed + Math.random() * (maxSpeed - minSpeed)
    
    return {
      text,
      x,
      y,
      opacity: 0.3 + Math.random() * 0.2, // более прозрачные
      speed,
      offsetX: 0,
      offsetY: 0,
      delay: index * 0.1, // задержка для анимации
      initial: true // для анимации появления
    }
  })
}

onMounted(() => {
  // Генерация звёзд
  for (let i = 0; i < 40; i++) {
    parallaxStars.value.push({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      opacity: 0.4 + Math.random() * 0.6,
      speed: 0.02 + Math.random() * 0.03,
      depth: Math.random() // 0 = ближе, 1 = дальше
    })
  }

  // Генерация фрагментов
  scriptFragments.value = generateFragmentPositions()
  
  // Анимация появления фрагментов
  setTimeout(() => {
    scriptFragments.value.forEach(frag => {
      frag.initial = false
    })
  }, 500)
  
  // Получаем размеры контента для точного позиционирования
  const contentElement = document.querySelector('.max-w-md')
  if (contentElement) {
    const rect = contentElement.getBoundingClientRect()
    contentRect.value = {
      width: rect.width,
      height: rect.height
    }
  }
  
  // Обновляем позиции при изменении размера окна
  window.addEventListener('resize', () => {
    scriptFragments.value = generateFragmentPositions()
    
    const contentElement = document.querySelector('.max-w-md')
    if (contentElement) {
      const rect = contentElement.getBoundingClientRect()
      contentRect.value = {
        width: rect.width,
        height: rect.height
      }
    }
  })
})

const handleMouseMove = (e) => {
  mousePosition.x = e.clientX
  mousePosition.y = e.clientY

  // Параллакс для звёзд
  parallaxStars.value.forEach(star => {
    const depthFactor = 1 - star.depth * 0.8
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
  const rotateFactor = 15
  rotateY.value = ((e.clientX - centerX) / rect.width) * rotateFactor
  rotateX.value = ((centerY - e.clientY) / rect.height) * rotateFactor
  scale404.value = 1.05
  glowIntensity.value = 0.8
}

const handleMouseLeave = () => {
  rotateX.value = 0
  rotateY.value = 0
  scale404.value = 1
  glowIntensity.value = 0.5
}

const handle404Click = () => {
  // Лёгкий "всплеск"
  scale404.value = 1.2
  glowIntensity.value = 1
  setTimeout(() => {
    scale404.value = 1
    glowIntensity.value = 0.5
  }, 300)
}
</script>

<style scoped>
/* Завихрения */
.swirl {
  position: absolute;
  width: 240px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 50%, rgba(253, 224, 71, 0.06) 0%, transparent 80%);
  opacity: 0.8;
  filter: blur(1px);
  z-index: 1;
  animation: swirl 30s linear infinite;
}
.swirl-1 { top: 10%; left: 5%; animation-duration: 25s; }
.swirl-2 { bottom: 15%; right: 10%; animation-duration: 35s; animation-direction: reverse; }
.swirl-3 { top: 50%; right: 20%; animation-duration: 40s; }

/* Параллакс-звёзды */
.parallax-star {
  position: absolute;
  background: #fde047;
  border-radius: 50%;
  pointer-events: none;
  transition: transform 0.1s ease-out;
  box-shadow: 0 0 10px #fde047, 0 0 20px rgba(253, 224, 71, 0.5);
}

/* Фрагменты сценария */
.script-fragment {
  position: absolute;
  color: rgba(253, 224, 71, 0.8);
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  letter-spacing: -0.5px;
  opacity: v-bind('fragment.opacity');
  pointer-events: none;
  transition: transform 0.1s ease-out, opacity 0.5s ease;
  max-width: 150px;
  word-wrap: break-word;
  text-align: center;
  text-shadow: 0 0 8px rgba(253, 224, 71, 0.8);
  z-index: 5;
  animation-delay: var(--delay);
}

/* Анимации для фрагментов */
.animate-fade-in {
  animation: fadeIn 1s forwards;
}

.animate-slide-in {
  animation: slideIn 15s infinite alternate;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  to { opacity: v-bind('fragment.opacity'); transform: translate(-50%, -50%) scale(1); }
}

@keyframes slideIn {
  0% { transform: translate(calc(-50% + v-bind('fragment.offsetX')px), calc(-50% + v-bind('fragment.offsetY')px)); }
  100% { transform: translate(calc(-50% + v-bind('fragment.offsetX')px * 1.5), calc(-50% + v-bind('fragment.offsetY')px * 1.5)); }
}

@keyframes swirl {
  0% { transform: rotate(0deg) scale(1); }
  100% { transform: rotate(360deg) scale(1.05); }
}

/* Адаптивность для мобильных устройств */
@media (max-width: 640px) {
  .script-fragment {
    font-size: 0.65rem;
    max-width: 120px;
  }
  
  /* На мобильных смещаем фрагменты ближе к краям */
  .script-fragment:nth-child(odd) {
    left: calc(var(--x) * 1% - 10%) !important;
  }
  .script-fragment:nth-child(even) {
    left: calc(var(--x) * 1% + 10%) !important;
  }
}
</style>