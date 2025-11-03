import { ref, computed } from "vue"
import { usePhoneAuth } from "~/src/entities/User/api/usePhoneAuth"

export type PhoneVerificationStep = "phone" | "code" | "success"

export function usePhoneVerification() {
  const {
    sendVerificationCode,
    verifyCode,
    errors,
    isLoading,
    phoneNumber,
    verificationCode,
    isError,
    clearErrors,
    resetState,
  } = usePhoneAuth()

  // UI state
  const currentStep = ref<PhoneVerificationStep>("phone")
  const timeRemaining = ref(300) // 5 minutes in seconds
  const resendCooldown = ref(0) // Cooldown for resend button (60 seconds)
  const timerInterval = ref<NodeJS.Timeout | null>(null)
  const resendInterval = ref<NodeJS.Timeout | null>(null)

  // Computed
  const canResend = computed(() => resendCooldown.value === 0)
  const formattedTime = computed(() => {
    const minutes = Math.floor(timeRemaining.value / 60)
    const seconds = timeRemaining.value % 60
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  })

  // Start expiry timer
  function startExpiryTimer() {
    stopExpiryTimer() // Clear any existing timer
    timeRemaining.value = 300 // Reset to 5 minutes

    timerInterval.value = setInterval(() => {
      if (timeRemaining.value > 0) {
        timeRemaining.value--
      } else {
        stopExpiryTimer()
        // Code has expired
        errors.value.code = ["Verification code has expired. Please request a new one."]
        currentStep.value = "phone"
      }
    }, 1000)
  }

  // Stop expiry timer
  function stopExpiryTimer() {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
      timerInterval.value = null
    }
  }

  // Start resend cooldown
  function startResendCooldown() {
    stopResendCooldown() // Clear any existing cooldown
    resendCooldown.value = 60 // 60 seconds

    resendInterval.value = setInterval(() => {
      if (resendCooldown.value > 0) {
        resendCooldown.value--
      } else {
        stopResendCooldown()
      }
    }, 1000)
  }

  // Stop resend cooldown
  function stopResendCooldown() {
    if (resendInterval.value) {
      clearInterval(resendInterval.value)
      resendInterval.value = null
    }
  }

  // Validate phone number format
  function validatePhone(phone: string): boolean {
    // Basic validation: starts with + and has at least 10 digits
    const phoneRegex = /^\+\d{10,15}$/
    return phoneRegex.test(phone)
  }

  // Send verification code
  async function sendCode(phone: string): Promise<boolean> {
    clearErrors()

    // Validate phone format
    if (!validatePhone(phone)) {
      errors.value.phone = ["Please enter a valid phone number (e.g., +1234567890)"]
      return false
    }

    try {
      await sendVerificationCode(phone)
      currentStep.value = "code"
      startExpiryTimer()
      startResendCooldown()
      return true
    } catch (error) {
      console.error("Error sending code:", error)
      return false
    }
  }

  // Verify code
  async function verify(phone: string, code: string): Promise<boolean> {
    clearErrors()

    // Validate code format (6 digits)
    if (!/^\d{6}$/.test(code)) {
      errors.value.code = ["Please enter a valid 6-digit code"]
      return false
    }

    try {
      await verifyCode(phone, code)
      currentStep.value = "success"
      stopExpiryTimer()
      stopResendCooldown()
      return true
    } catch (error) {
      console.error("Error verifying code:", error)
      return false
    }
  }

  // Resend verification code
  async function resendCode(): Promise<boolean> {
    if (!canResend.value) {
      return false
    }

    clearErrors()

    try {
      await sendVerificationCode(phoneNumber.value)
      startExpiryTimer()
      startResendCooldown()
      return true
    } catch (error) {
      console.error("Error resending code:", error)
      return false
    }
  }

  // Reset to initial state
  function reset() {
    stopExpiryTimer()
    stopResendCooldown()
    resetState()
    currentStep.value = "phone"
    timeRemaining.value = 300
    resendCooldown.value = 0
  }

  // Cancel and go back to phone entry
  function cancel() {
    stopExpiryTimer()
    stopResendCooldown()
    clearErrors()
    currentStep.value = "phone"
    verificationCode.value = ""
  }

  return {
    // State
    currentStep,
    phoneNumber,
    verificationCode,
    errors,
    isLoading,
    timeRemaining,
    resendCooldown,
    canResend,
    formattedTime,

    // Methods
    sendCode,
    verify,
    resendCode,
    reset,
    cancel,
    isError,
  }
}
