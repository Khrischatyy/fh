import { navigateTo } from "nuxt/app"
import { useCookie } from "#app"

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
      404: "Page not found",
      422: "Validation error", // Specific message for validation errors
      500: "Server error",
    }

    if (status === 404) {
      if (process.client) {
        navigateTo("/404")
      }
      return Promise.reject({ status, message: "Redirecting to 404 page" })
    }

    if (status === 401) {
      const { useSessionStore } = await import("~/src/entities/Session")
      const sessionStore = useSessionStore()
      sessionStore.setAuthorized(false)
      sessionStore.setAccessToken(null)
      if (process.client) {
        navigateTo("/login")
      }
      return Promise.resolve({ status, message: "Redirecting to login page" })
    }

    // Check for specific error messages from the server
    if (errorData) {
      if (errorData.errors) {
        // Server provided specific field errors
        return Promise.reject({
          status: status,
          message: errorData.message,
          errors: errorData.errors,
        })
      } else if (errorData.message) {
        // Server provided a general error message
        return Promise.reject({
          status: status,
          message: errorData.message,
        })
      }
    }

    // Default error handling if no specific messages are found
    const message = nativeMessages[status] || errorData
    return Promise.reject({ status, message })
  }
}
