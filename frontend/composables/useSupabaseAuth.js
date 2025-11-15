export const useSupabaseAuth = () => {
  const user = useSupabaseUser()
  const client = useSupabaseClient()
  const router = useRouter()

  // Вход через email/password
  const signIn = async (email, password) => {
    try {
      const { error } = await client.auth.signInWithPassword({ email, password })
      if (error) throw error
      await router.push('/dashboard')
    } catch (error) {
      throw new Error(error.message || 'Ошибка входа')
    }
  }

  // Регистрация
  const signUp = async (email, password, metadata = {}) => {
    try {
      const { error } = await client.auth.signUp({
        email,
        password,
        options: { 
          data: metadata,
          // Отключаем подтверждение email для хакатона (опционально)
          // emailRedirectTo: `${window.location.origin}/login`
        }
      })
      if (error) throw error
    } catch (error) {
      throw new Error(error.message || 'Ошибка регистрации')
    }
  }

  // Выход
  const signOut = async () => {
    try {
      const { error } = await client.auth.signOut()
      if (error) throw error
      await router.push('/login')
    } catch (error) {
      throw new Error(error.message || 'Ошибка выхода')
    }
  }

  // Проверка аутентификации
  const requireAuth = () => {
    if (!user.value) {
      router.push('/login')
      return false
    }
    return true
  }

  return {
    user,
    signIn,
    signUp,
    signOut,
    requireAuth
  }
}