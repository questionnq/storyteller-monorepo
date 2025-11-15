<template>
  <header 
    class="navbar relative bg-gradient-to-r from-indigo-950/95 via-purple-950/95 to-blue-950/95 backdrop-blur-md shadow-lg sticky top-0 z-50 border-b border-yellow-400/20 overflow-visible"
  >
    <div class="navbar-start">
      <NuxtLink 
        to="/dashboard" 
        class="btn btn-ghost normal-case text-xl flex items-center gap-2.5 group"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" class="text-yellow-300 group-hover:text-yellow-200 transition-colors duration-300 drop-shadow-[0_0_6px_rgba(253,224,71,0.5)]" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
        <span class="font-medium">
          <span class="text-yellow-200">Storyteller</span>
          <span class="text-slate-100">AI</span>
        </span>
      </NuxtLink>
    </div>
    
    <div class="navbar-center hidden lg:flex">
      <ul class="menu menu-horizontal px-1 gap-2">
        <li>
          <NuxtLink 
            to="/dashboard" 
            class="flex items-center gap-2 px-4 py-2.5 rounded-2xl font-medium text-slate-200 hover:text-yellow-200 transition-all duration-300 relative group"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
              <path d="M12 13v6" />
              <path d="M15 16l-3-3-3 3" />
            </svg>
            <span>Мои проекты</span>
          </NuxtLink>
        </li>
        <li>
          <a 
            href="#" 
            @click.prevent="createNewProject"
            class="flex items-center gap-2 px-4 py-2.5 rounded-2xl font-medium text-slate-200 hover:text-yellow-200 transition-all duration-300 relative group"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="16" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
            <span>Новый проект</span>
          </a>
        </li>
      </ul>
    </div>
    
    <div class="navbar-end">
      <div v-if="user">
        <div class="relative" ref="dropdown">
          <button @click="toggleMenu" class="btn btn-ghost btn-circle">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-300 to-blue-500 flex items-center justify-center text-white font-bold border border-yellow-300/40">
              {{ user.email?.charAt(0).toUpperCase() }}
            </div>
          </button>
          <div v-show="menuOpen" class="absolute right-0 mt-2 w-56 p-3 shadow-xl bg-gradient-to-br from-indigo-900/95 to-purple-900/95 backdrop-blur-md rounded-2xl border border-yellow-400/20 z-20">
            <div class="text-slate-200 text-sm mb-2 px-1 truncate">{{ user.email }}</div>
            <button @click="handleSignOut" class="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-slate-200 hover:text-yellow-200 transition-colors text-left">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              Выйти
            </button>
          </div>
        </div>
      </div>
      <div v-else class="w-10"></div>
    </div>
  </header>
</template>

<script setup>
const { user, signOut } = useSupabaseAuth()
const router = useRouter()

const menuOpen = ref(false)
const dropdown = ref(null)

const createNewProject = () => {
  router.push('/project/new')
}

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
  if (menuOpen.value) {
    setTimeout(() => {
      const handleClickOutside = (e) => {
        if (dropdown.value && !dropdown.value.contains(e.target)) {
          menuOpen.value = false
          window.removeEventListener('click', handleClickOutside)
        }
      }
      window.addEventListener('click', handleClickOutside)
    }, 0)
  }
}

const handleSignOut = async () => {
  menuOpen.value = false
  await signOut()
}
</script>

<style scoped>

header {
  transition: background 0.3s, border-color 0.3s;
}
</style>