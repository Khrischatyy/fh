import { reactive, ref } from "vue"
import { useApi } from "~/src/lib/api"
import { useSessionStore } from "~/src/entities/Session"
import { navigateTo } from "nuxt/app"

type registerValues = {
  name: string
  email: string
  password: string
  password_confirmation: string
  role: string
}
type ErrorType = {
  name?: string[]
  email?: string[]
  password?: string[]
  password_confirmation?: string[]
  role?: string[]
}

type ErrorField =
  | "name"
  | "email"
  | "password"
  | "password_confirmation"
  | "role" // Add other field names as needed

export function useCreateAccount() {
  const formValues = reactive({
    name: "",
    email: "",
    password: "",
    password_confirmation: "",
    role: "",
  })

  const errors = ref<ErrorType>({})
  const isLoading = ref(false)

  function isError(field: ErrorField): string | boolean {
    if (errors.value.hasOwnProperty(field)) {
      const errorMessages = errors.value[field]
      if (errorMessages && errorMessages.length > 0) {
        return errorMessages[0] // Return the first error message
      }
    }
    return false // Return false if no errors are found
  }
  async function registerUser(data: registerValues) {
    const session = useSessionStore()
    const formData = new FormData()
    Object.keys(data).forEach((key: any) => {
      if (key in data) {
        const value = data[key as keyof registerValues]
        if (value !== null) {
          formData.append(key, value as string | Blob)
        }
      }
    })

    const { post } = useApi({
      url: "/auth/register",
      auth: false,
    })

    // Clear previous errors before a new submission
    errors.value = {}

    try {
      const response = await post(formData)

      session.setUserRole(response?.role)
      session.authorize(response?.token)

      if (response?.role === "studio_owner" && !response?.has_company) {
        navigateTo("/create")
      } else {
        navigateTo("/")
      }

      return response
    } catch (error: any) {
      console.error("Failed to create studio:", error)
      if (error.errors) {
        // Update UI or state with specific field errors
        errors.value = error.errors
      } else {
        // Handle general error message
        errors.value.general = [error.message]
      }
      throw error // Rethrow the error to allow further handling
    } finally {
      isLoading.value = false
    }
  }

  return { registerUser, errors, isLoading, formValues, isError }
}
