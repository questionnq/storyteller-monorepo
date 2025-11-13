<template>
  <ClientOnly>
    <Teleport to="body">
      <div v-if="isOpen" class="modal modal-open">
        <div class="modal-box">
          <h3 class="font-bold text-lg mb-4">{{ dialogTitle }}</h3>
          <p class="py-4">{{ dialogMessage }}</p>
          <div class="modal-action">
            <button class="btn btn-ghost" @click="handleCancel">
              Отмена
            </button>
            <button class="btn btn-error" @click="handleConfirm">
              Удалить
            </button>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop" @click.prevent="handleCancel">
          <button>close</button>
        </form>
      </div>
    </Teleport>
  </ClientOnly>
</template>

<script setup>
import { useConfirm } from '~/composables/useConfirm'

const { isOpen, dialogTitle, dialogMessage, handleConfirm, handleCancel } = useConfirm()
</script>
