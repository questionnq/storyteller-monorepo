import { ref } from 'vue'

const notification = ref({
  show: false,
  message: '',
  type: 'error'
})

export const useNotification = () => {
  const show = (message, type = 'error') => {
    notification.value = {
      show: true,
      message,
      type
    }
  }
  
  const close = () => {
    notification.value.show = false
  }
  
  const showError = (message) => show(message, 'error')
  const showSuccess = (message) => show(message, 'success')
  const showInfo = (message) => show(message, 'info')

  return {
    notification: readonly(notification),
    show,
    close,
    showError,
    showSuccess,
    showInfo
  }
}