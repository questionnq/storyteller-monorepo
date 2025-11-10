<template>
  <div class="flex flex-col items-center justify-center p-8 text-center">
    <span class="loading loading-spinner loading-lg text-primary mb-4"></span>
    <p class="text-lg font-semibold">{{ title }}</p>
    <p class="text-sm opacity-70 mt-2">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Загрузка...' },
  subtitle: { type: String, default: 'Подождите немного' }
})
</script>