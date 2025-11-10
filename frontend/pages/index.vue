<template>
  <div class="hero min-h-screen bg-base-200">
    <div class="hero-content text-center">
      <div class="max-w-md">
        <h1 class="text-5xl font-bold">
          <span class="text-primary">Storyboard</span>
          <span class="text-base-content">AI</span>
        </h1>
        <p class="py-6">
          Генерируй сценарии и визуальные раскадровки за минуты с помощью ИИ
        </p>
        
        <div class="flex gap-4 justify-center flex-col sm:flex-row">
          <NuxtLink to="/dashboard" class="btn btn-primary btn-lg">
            Начать работу
          </NuxtLink>
          <NuxtLink v-if="!user" to="/login" class="btn btn-outline btn-lg">
            Войти
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
</script>