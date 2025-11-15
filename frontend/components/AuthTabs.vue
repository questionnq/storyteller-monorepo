<template>
  <div class="tabs tabs-boxed justify-center mb-6">
    <NuxtLink 
      to="/login" 
      class="tab"
      :class="{ 'tab-active': route.path === '/login' }"
    >
      Вход
    </NuxtLink>
    <NuxtLink 
      to="/register" 
      class="tab"
      :class="{ 'tab-active': route.path === '/register' }"
    >
      Регистрация
    </NuxtLink>
  </div>
</template>

<script setup>
const route = useRoute()
</script>