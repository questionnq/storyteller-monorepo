<template>
  <div class="min-h-screen bg-base-100">
    <!-- Глобальное уведомление -->
    <Notification />
    
    <!-- ЕДИНСТВЕННЫЙ AppHeader на всех страницах -->
    <AppHeader />
    
    <!-- Контент страниц -->
    <main class="pb-8">
      <slot />
    </main>
  </div>
</template>