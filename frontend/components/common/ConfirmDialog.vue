<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-black bg-opacity-50"
      @click="handleCancel"
    ></div>

    <!-- Modal -->
    <div class="relative bg-base-100 rounded-lg shadow-xl p-6 max-w-md w-full mx-4 z-10">
      <h3 class="font-bold text-lg mb-4">{{ dialogTitle }}</h3>
      <p class="py-4">{{ dialogMessage }}</p>
      <div class="flex justify-end gap-3 mt-6">
        <button class="btn btn-ghost" @click="handleCancel">
          Отмена
        </button>
        <button class="btn btn-error" @click="handleConfirm">
          Удалить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useConfirm } from '~/composables/useConfirm'

const { isOpen, dialogTitle, dialogMessage, handleConfirm, handleCancel } = useConfirm()

// Debug
watch(isOpen, (val) => {
  console.log('[ConfirmDialog] isOpen changed:', val)
})
</script>
