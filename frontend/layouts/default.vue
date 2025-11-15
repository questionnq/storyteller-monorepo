<template>
  <div class="min-h-screen">
    <Notification />
    <CommonConfirmDialog />
    <AppHeader />
    <main class="pb-8">
      <slot />
    </main>
  </div>
</template>