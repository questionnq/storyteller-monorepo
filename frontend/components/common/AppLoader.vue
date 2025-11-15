<template>
  <div class="flex flex-col items-center justify-center p-8 text-center animate-fade-in">
    <div class="loading-spinner mb-4">
      <div class="loading-inner"></div>
    </div>
    <p class="text-lg font-semibold text-slate-100">{{ title }}</p>
    <p class="text-sm text-slate-400 mt-2">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Загрузка...' },
  subtitle: { type: String, default: 'Подождите немного' }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fade-in 0.4s ease-out forwards;
  opacity: 0;
}
@keyframes fade-in {
  to { opacity: 1; }
}

.loading-spinner {
  width: 36px;
  height: 36px;
  position: relative;
}
.loading-inner {
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: #fde047;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  background: conic-gradient(
    transparent, 
    #fde047 20%, 
    #a78bfa 60%, 
    transparent 80%
  );
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 3px));
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>