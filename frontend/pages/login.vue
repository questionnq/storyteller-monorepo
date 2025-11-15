<template>
  <NuxtLayout name="auth">
    <div 
      class="hero min-h-screen relative overflow-hidden bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950"
      @mousemove="handleMouseMove"
      @mouseleave="handleMouseLeave"
    >
      <div class="absolute inset-0 overflow-hidden">
        <div v-for="i in 60" :key="i" class="auth-star" :style="getStarStyle(i)"></div>
      </div>

      <div class="absolute inset-0 overflow-hidden">
        <div class="auth-swirl" style="top: 10%; left: 5%; width: 250px; height: 120px; animation: swirl 30s linear infinite;"></div>
        <div class="auth-swirl" style="bottom: 15%; right: 10%; width: 280px; height: 140px; animation: swirl 35s reverse linear infinite;"></div>
        <div class="auth-swirl" style="top: 50%; right: 20%; width: 220px; height: 110px; animation: swirl 40s linear infinite;"></div>
      </div>

      <div 
        class="absolute inset-0 opacity-20 pointer-events-none"
        :style="{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(253, 224, 71, 0.15) 0%, transparent 60%)`
        }"
      ></div>

      <div class="van-gogh-texture opacity-8"></div>

      <div class="hero-content flex-col lg:flex-row-reverse relative z-10 px-4">
        <div class="text-center lg:text-left max-w-lg fade-in-left">
          <h1 class="text-5xl font-bold mb-2">
            <span class="text-yellow-200 drop-shadow-[0_0_8px_rgba(253,224,71,0.4)]">Storyteller</span>
            <span class="text-slate-100">AI</span>
          </h1>
          <p class="py-6 text-slate-200">Войдите, чтобы создавать сценарии и видео с помощью ИИ</p>
        </div>

        <div class="auth-card w-full max-w-sm">
          <div 
            class="card rounded-3xl p-8 border border-yellow-400/30 bg-gradient-to-br from-amber-400/10 to-blue-500/15 backdrop-blur-xl shadow-2xl card-glow"
          >
            <div class="card-body p-0">
              <AuthTabs />

              <form @submit.prevent="handleLogin" class="space-y-5">
                <div class="form-control">
                  <label class="label p-0 mb-2">
                    <span class="label-text text-slate-200 font-medium flex items-center gap-2">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                        <polyline points="22,6 12,13 2,6" />
                      </svg>
                      Email
                    </span>
                  </label>
                  <input 
                    v-model="email" 
                    type="email" 
                    placeholder="you@example.com" 
                    class="w-full px-4 py-3 bg-slate-800/50 border border-yellow-400/30 rounded-2xl text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 transition-all"
                    required
                  />
                </div>
                
                <div class="form-control">
                  <label class="label p-0 mb-2">
                    <span class="label-text text-slate-200 font-medium flex items-center gap-2">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                        <path d="M7 11V7a5 5 0 0110 0v4" />
                      </svg>
                      Пароль
                    </span>
                    <a href="#" class="label-text-alt text-yellow-300 hover:text-yellow-200 transition-colors text-sm">Забыли пароль?</a>
                  </label>
                  <input 
                    v-model="password" 
                    type="password" 
                    placeholder="••••••••" 
                    class="w-full px-4 py-3 bg-slate-800/50 border border-yellow-400/30 rounded-2xl text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 transition-all"
                    required
                  />
                </div>
                
                <div class="form-control mt-6">
                  <button 
                    class="btn btn-van-gogh-primary btn-block py-3 relative overflow-hidden group"
                    type="submit"
                    :disabled="loading"
                  >
                    <span v-if="!loading" class="relative z-10">Войти</span>
                    <span v-else class="flex items-center justify-center">
                      <span class="loading loading-spinner loading-sm text-white"></span>
                    </span>
                  </button>
                </div>
                
                <div v-if="error" class="mt-4 p-3 rounded-2xl bg-red-900/30 border border-red-500/40 text-red-200 text-sm">
                  {{ error }}
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
definePageMeta({ layout: 'auth' })

const { signIn } = useSupabaseAuth()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const mousePosition = reactive({ x: 0, y: 0 })

function handleMouseMove(e) {
  mousePosition.x = e.clientX
  mousePosition.y = e.clientY
}

function handleMouseLeave() {
}

function getStarStyle(index) {
  const size = Math.random() * 2 + 0.8
  const left = Math.random() * 100
  const top = Math.random() * 100
  const delay = Math.random() * 4
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`
  }
}

const handleLogin = async () => {
  loading.value = true
  error.value = null
  try {
    await signIn(email.value, password.value)
  } catch (err) {
    error.value = err.message || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>