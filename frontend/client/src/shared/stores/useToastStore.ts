import { defineStore } from "pinia"

export type ToastType = "error" | "success" | "warning" | "info"

interface ToastState {
  message: string
  type: ToastType
  isVisible: boolean
  timeoutId: NodeJS.Timeout | null
}

export const useToastStore = defineStore({
  id: "toast-store",
  state: (): ToastState => ({
    message: "",
    type: "error",
    isVisible: false,
    timeoutId: null,
  }),
  actions: {
    show(message: string, type: ToastType = "error", duration: number = 5000) {
      // Clear any existing timeout
      if (this.timeoutId) {
        clearTimeout(this.timeoutId)
      }

      this.message = message
      this.type = type
      this.isVisible = true

      // Auto-hide after duration
      if (duration > 0) {
        this.timeoutId = setTimeout(() => {
          this.hide()
        }, duration)
      }
    },
    hide() {
      this.isVisible = false
      this.message = ""
      if (this.timeoutId) {
        clearTimeout(this.timeoutId)
        this.timeoutId = null
      }
    },
    error(message: string, duration?: number) {
      this.show(message, "error", duration)
    },
    success(message: string, duration?: number) {
      this.show(message, "success", duration)
    },
    warning(message: string, duration?: number) {
      this.show(message, "warning", duration)
    },
    info(message: string, duration?: number) {
      this.show(message, "info", duration)
    },
  },
})
