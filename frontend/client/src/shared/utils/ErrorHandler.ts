import { navigateTo } from "nuxt/app"
import { useCookie } from "#app"
import { useToastStore } from "~/src/shared/stores/useToastStore"
import { useSessionStore } from "~/src/entities/Session"

interface ApiResponse {
  status: number
  message: string
  errors?: Record<string, any>
}

function safeStringify(obj: any, space: number = 2) {
  const cache = new Set()
  return JSON.stringify(
    obj,
    (key, value) => {
      if (typeof value === "object" && value !== null) {
        if (cache.has(value)) {
          return // Duplicate reference found, discard key
        }
        cache.add(value)
      }
      return value
    },
    space,
  )
}

export class ErrorHandler {
  public static async handleApiError(
    error: any,
  ): Promise<Awaited<{ message: string; status: any }>> {
    // Log the error without causing a circular reference issue
    try {
      console.error("API Error:", safeStringify(error))
    } catch (e) {
      console.error("Error logging failed:", e)
    }

    // Extract the error response
    const response: ApiResponse = error.response?._data || error.response
    const status = response?.status || error.response?.status
    const errorData = response

    // Define common error messages based on status codes
    const nativeMessages: Record<number, string> = {
      401: "Authorization error",
      404: "Resource not found",
      422: "Validation error",
      500: "Server error",
    }

    // Show toast for errors instead of redirecting (except 401)
    const showErrorToast = (message: string) => {
      if (process.client) {
        try {
          const toastStore = useToastStore()
          toastStore.error(message)
        } catch (e) {
          // Fallback if toast store not available
          console.error("Toast error:", message)
        }
      }
    }

    if (status === 404) {
      // Don't redirect to 404 page - show toast instead
      const message = errorData?.message || nativeMessages[404]
      showErrorToast(message)
      return Promise.reject({ status, message })
    }

    if (status === 401) {
      if (process.client) {
        const sessionStore = useSessionStore()
        sessionStore.setAuthorized(false)
        sessionStore.setAccessToken(null)
        navigateTo("/login")
      }
      return Promise.resolve({ status, message: "Redirecting to login page" })
    }

    // Check for specific error messages from the server
    if (errorData) {
      if (errorData.errors) {
        // Server provided specific field errors - show first error in toast
        const firstError = Object.values(errorData.errors)[0]
        const errorMessage = Array.isArray(firstError) ? firstError[0] : firstError
        showErrorToast(errorMessage || errorData.message)
        return Promise.reject({
          status: status,
          message: errorData.message,
          errors: errorData.errors,
        })
      } else if (errorData.message) {
        // Server provided a general error message
        showErrorToast(errorData.message)
        return Promise.reject({
          status: status,
          message: errorData.message,
        })
      }
    }

    // Default error handling if no specific messages are found
    const message = nativeMessages[status] || "An unexpected error occurred"
    showErrorToast(message)
    return Promise.reject({ status, message })
  }
}
