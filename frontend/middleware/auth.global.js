// middleware/auth.global.js
export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser()
  
  // Публичные страницы (доступны без авторизации)
  const publicPages = ['/', '/login', '/register']
  
  if (publicPages.includes(to.path)) {
    return
  }
  
  // Если неавторизован - редирект на логин
  if (!user.value) {
    return navigateTo('/login')
  }
})