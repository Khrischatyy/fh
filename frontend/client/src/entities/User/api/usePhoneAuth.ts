import { ref } from "vue"
import { useApi } from "~/src/lib/api"
import { useSessionStore } from "~/src/entities/Session"
import { navigateTo } from "nuxt/app"

type SendCodeRequest = {
  phone: string
}

type VerifyCodeRequest = {
  phone: string
  code: string
}

type SendCodeResponse = {
  message: string
  phone: string
  expires_in: number
}

type VerifyCodeResponse = {
  message: string
  token: string
  role: string
  user_id: number
  is_new_user: boolean
}

type ErrorType = {
  phone?: string[]
  code?: string[]
  general?: string[]
}

type ErrorField = "phone" | "code" | "general"

export function usePhoneAuth() {
  const errors = ref<ErrorType>({})
  const isLoading = ref(false)
  const phoneNumber = ref("")
  const verificationCode = ref("")

  function isError(field: ErrorField): string | boolean {
    if (errors.value.hasOwnProperty(field)) {
      const errorMessages = errors.value[field]
      if (errorMessages && errorMessages.length > 0) {
        return errorMessages[0] // Return the first error message
      }
    }
    return false // Return false if no errors are found
  }

  async function sendVerificationCode(phone: string): Promise<SendCodeResponse> {
    isLoading.value = true
    errors.value = {} // Clear previous errors

    const { post } = useApi({
      url: "/auth/sms/send",
      auth: false,
    })

    try {
      const response = await post({ phone })
      phoneNumber.value = phone // Store phone for later verification
      return response as SendCodeResponse
    } catch (error: any) {
      console.error("Failed to send verification code:", error)
      if (error.errors) {
        errors.value = error.errors
      } else {
        errors.value.general = [error.message || "Failed to send verification code"]
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function verifyCode(
    phone: string,
    code: string
  ): Promise<VerifyCodeResponse> {
    isLoading.value = true
    errors.value = {} // Clear previous errors

    const session = useSessionStore()

    const { post } = useApi({
      url: "/auth/sms/verify",
      auth: false,
    })

    try {
      const response = await post({ phone, code }) as VerifyCodeResponse

      // Store authentication data
      session.setUserRole(response.role)
      session.authorize(response.token)

      // Resume booking if there is any stored data
      const storedBookingData = localStorage.getItem("bookingData")
      if (storedBookingData) {
        navigateTo("/booking-resume")
        return response
      }

      // Navigate based on role and company status
      if (response.role === "studio_owner" && response.is_new_user) {
        navigateTo("/create") // New studio owner needs to create company
      } else {
        navigateTo("/") // Regular user or existing user
      }

      return response
    } catch (error: any) {
      console.error("Failed to verify code:", error)
      if (error.errors) {
        errors.value = error.errors
      } else {
        errors.value.general = [error.message || "Failed to verify code"]
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  function clearErrors() {
    errors.value = {}
  }

  function resetState() {
    errors.value = {}
    isLoading.value = false
    phoneNumber.value = ""
    verificationCode.value = ""
  }

  return {
    // State
    errors,
    isLoading,
    phoneNumber,
    verificationCode,

    // Methods
    sendVerificationCode,
    verifyCode,
    isError,
    clearErrors,
    resetState,
  }
}
