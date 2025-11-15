<template>
  <div>
    <div v-if="isOpen" class="fixed inset-0 z-[9999] flex items-center justify-center">
      <!-- Размытый бэкдроп -->
      <div
        class="fixed inset-0 bg-black/40 backdrop-blur-sm"
        @click="handleCancel"
      ></div>

      <!-- Модалка -->
      <div 
        class="relative rounded-2xl p-6 max-w-md w-full mx-4 z-10 animate-modal-pop"
      >
        <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/40 backdrop-blur-lg border border-yellow-400/30 rounded-2xl p-6">
          <h3 class="font-bold text-slate-100 text-lg mb-3">{{ dialogTitle }}</h3>
          <p class="text-slate-300 py-2">{{ dialogMessage }}</p>
          
          <div class="flex justify-end gap-3 mt-6">
            <button 
              class="btn btn-ghost btn-sm px-4 py-2 text-slate-300 hover:text-slate-100 border border-slate-700 rounded-lg transition-colors"
              @click="handleCancel"
            >
              Отмена
            </button>
            <button 
              class="btn btn-sm px-4 py-2 text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 rounded-lg shadow-sm transition-all border-0"
              @click="handleConfirm"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { isOpen, dialogTitle, dialogMessage, handleConfirm, handleCancel } = useConfirm()
</script>

<style scoped>
.animate-modal-pop {
  animation: modal-pop 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

@keyframes modal-pop {
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>