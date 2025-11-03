<script setup lang="ts">
import { ref, watch } from "vue"
import { FInputClassic } from "~/src/shared/ui/common/Input"
import { usePhoneVerification } from "../model/usePhoneVerification"

const emit = defineEmits<{
  success: [token: string]
  cancel: []
}>()

const {
  currentStep,
  phoneNumber,
  verificationCode,
  errors,
  isLoading,
  timeRemaining,
  resendCooldown,
  canResend,
  formattedTime,
  sendCode,
  verify,
  resendCode,
  cancel,
  isError,
} = usePhoneVerification()

const localPhone = ref("")
const localCode = ref("")

// Auto-submit when 6 digits entered
watch(localCode, (newCode) => {
  if (newCode.length === 6 && /^\d{6}$/.test(newCode)) {
    handleVerify()
  }
})

async function handleSendCode() {
  const success = await sendCode(localPhone.value)
  if (success) {
    phoneNumber.value = localPhone.value
  }
}

async function handleVerify() {
  const success = await verify(localPhone.value, localCode.value)
  if (success) {
    // Emit success event to parent
    emit("success", "authenticated")
  }
}

async function handleResend() {
  await resendCode()
}

function handleCancel() {
  cancel()
  emit("cancel")
}
</script>

<template>
  <div class="phone-auth-container w-full max-w-96">
    <!-- Step 1: Phone Entry -->
    <div v-if="currentStep === 'phone'" class="phone-entry-step space-y-4">
      <FInputClassic
        v-model="localPhone"
        label="Phone Number"
        placeholder="+1234567890"
        type="tel"
        :error="isError('phone')"
        :disabled="isLoading"
        size="md"
      />

      <div class="flex gap-2">
        <button
          @click="handleSendCode"
          :disabled="isLoading || !localPhone"
          class="flex-1 px-6 py-3 bg-white text-black rounded-lg font-medium hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="isLoading">Sending...</span>
          <span v-else>Send Code</span>
        </button>
      </div>

      <p class="text-xs text-white/60 text-center">
        Enter your phone number in international format (e.g., +1234567890)
      </p>
    </div>

    <!-- Step 2: Code Verification -->
    <div v-if="currentStep === 'code'" class="code-entry-step space-y-4">
      <div class="text-sm text-white/80 mb-4">
        <p>Code sent to {{ localPhone }}</p>
        <p class="text-xs text-white/60 mt-1">Expires in {{ formattedTime }}</p>
      </div>

      <FInputClassic
        v-model="localCode"
        label="Verification Code"
        placeholder="123456"
        type="text"
        maxlength="6"
        :error="isError('code')"
        :disabled="isLoading"
        size="md"
      />

      <div class="flex gap-2">
        <button
          @click="handleVerify"
          :disabled="isLoading || localCode.length !== 6"
          class="flex-1 px-6 py-3 bg-white text-black rounded-lg font-medium hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="isLoading">Verifying...</span>
          <span v-else>Verify</span>
        </button>

        <button
          @click="handleCancel"
          :disabled="isLoading"
          class="px-6 py-3 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Cancel
        </button>
      </div>

      <button
        @click="handleResend"
        :disabled="!canResend || isLoading"
        class="w-full text-sm text-white/80 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="!canResend">Resend code in {{ resendCooldown }}s</span>
        <span v-else>Resend Code</span>
      </button>

      <p class="text-xs text-white/60 text-center">
        Enter the 6-digit code sent to your phone
      </p>
    </div>

    <!-- Success State -->
    <div v-if="currentStep === 'success'" class="success-state text-center py-4">
      <p class="text-white font-medium">✓ Authenticated successfully!</p>
      <p class="text-sm text-white/60 mt-2">Redirecting...</p>
    </div>

    <!-- General Error Display -->
    <div v-if="isError('general')" class="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg">
      <p class="text-sm text-red-300">{{ isError('general') }}</p>
    </div>
  </div>
</template>

<style scoped>
.phone-auth-container {
  /* Inherit styles from parent */
}
</style>
