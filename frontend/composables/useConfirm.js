// composables/useConfirm.js
let resolveCallback = null

export const useConfirm = () => {
  const isOpen = useState('confirm-dialog-open', () => false)
  const dialogTitle = useState('confirm-dialog-title', () => '')
  const dialogMessage = useState('confirm-dialog-message', () => '')

  const confirm = (title, message) => {
    console.log('[useConfirm] confirm called:', { title, message })
    return new Promise((resolve) => {
      dialogTitle.value = title
      dialogMessage.value = message
      isOpen.value = true
      resolveCallback = resolve
      console.log('[useConfirm] modal opened, isOpen:', isOpen.value)
    })
  }

  const handleConfirm = () => {
    console.log('[useConfirm] handleConfirm called')
    isOpen.value = false
    if (resolveCallback) {
      resolveCallback(true)
      resolveCallback = null
    }
  }

  const handleCancel = () => {
    console.log('[useConfirm] handleCancel called')
    isOpen.value = false
    if (resolveCallback) {
      resolveCallback(false)
      resolveCallback = null
    }
  }

  return {
    isOpen,
    dialogTitle,
    dialogMessage,
    confirm,
    handleConfirm,
    handleCancel
  }
}
