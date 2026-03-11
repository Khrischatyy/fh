<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta } from "#imports"
import { ref, onMounted, computed } from "vue"
import { useApi } from "~/src/lib/api"
import { navigateTo, useRoute } from "nuxt/app"
import { Spinner } from "~/src/shared/ui/common"

useHead({
  title: "Funny How – Payment Success",
  meta: [{ name: "description", content: "Device Payment Successful" }],
})
definePageMeta({
  layout: "error",
})

const route = useRoute()
const isLoading = ref(true)
const errorMessage = ref("")
const successMessage = ref("")
const expiresAt = ref("")
const deviceName = ref("")
const devicePassword = ref("")
const showPassword = ref(false)
const passwordCopied = ref(false)

const sessionId = computed(() => route.query.session_id as string)
const deviceUuid = computed(() => route.query.device_uuid as string)

const copyPassword = async () => {
  try {
    await navigator.clipboard.writeText(devicePassword.value)
    passwordCopied.value = true
    setTimeout(() => { passwordCopied.value = false }, 2000)
  } catch (e) {
    console.error("Failed to copy password:", e)
  }
}

const processPayment = async () => {
  if (!sessionId.value || !deviceUuid.value) {
    errorMessage.value = "Invalid request parameters"
    isLoading.value = false
    return
  }

  try {
    const { fetch: paymentSuccess } = useApi({
      url: `/devices/payment-success?session_id=${sessionId.value}&device_uuid=${deviceUuid.value}`,
    })

    const response = await paymentSuccess()

    if (response.success) {
      successMessage.value = response.message || "Device unlocked successfully!"

      if (response.expires_at) {
        const date = new Date(response.expires_at)
        expiresAt.value = date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      }

      if (response.device_name) {
        deviceName.value = response.device_name
      }
      if (response.device_password) {
        devicePassword.value = response.device_password
      }
    } else {
      errorMessage.value = response.message || "Payment verification failed."
    }
  } catch (error: any) {
    errorMessage.value = error.message?.error || error.message || "Payment verification failed."
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await processPayment()
})
</script>

<template>
  <div class="w-full max-w-md px-4">
    <Spinner :is-loading="isLoading" />

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center">
      <div class="w-8 h-8 rounded-full bg-white/[0.08] flex items-center justify-center mx-auto mb-4">
        <div class="w-4 h-4 border-2 border-white/20 border-t-white/80 rounded-full animate-spin"></div>
      </div>
      <h2 class="text-base font-semibold text-white/90">Processing Payment...</h2>
      <p class="text-xs text-white/40 mt-1">Please wait while we verify your payment</p>
    </div>

    <!-- Success State -->
    <div v-else-if="successMessage && !errorMessage" class="flex flex-col items-center gap-6">
      <!-- Success Icon -->
      <div class="w-14 h-14 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center">
        <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <!-- Header -->
      <div class="text-center">
        <h2 class="text-base font-semibold text-white/90 mb-1">Payment Successful</h2>
        <p class="text-xs text-white/40">{{ successMessage }}</p>
      </div>

      <!-- Info Card -->
      <div class="w-full bg-neutral-900/60 border border-white/[0.06] rounded-[10px] p-5">
        <!-- Expires Info -->
        <div v-if="expiresAt" class="mb-4">
          <p class="text-xs text-white/40 mb-1">Device unlocked until</p>
          <p class="text-sm font-semibold text-white/90">{{ expiresAt }}</p>
        </div>

        <!-- Device Name -->
        <div v-if="deviceName" class="mb-4">
          <p class="text-xs text-white/40 mb-1">Device</p>
          <p class="text-sm font-medium text-white/80">{{ deviceName }}</p>
        </div>

        <!-- Device Password -->
        <div v-if="devicePassword">
          <p class="text-xs text-white/40 mb-2">Device Password</p>
          <div class="bg-black/40 border border-white/[0.06] rounded-lg px-4 py-3 flex items-center justify-between gap-3 mb-2">
            <code class="text-white/80 font-mono text-sm tracking-wider">{{ showPassword ? devicePassword : '••••••••' }}</code>
            <button
              @click="showPassword = !showPassword"
              class="text-[11px] text-white/30 shrink-0 hover:text-white/50 transition-colors"
            >
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <button
            @click="copyPassword"
            class="w-full py-2 rounded-lg text-xs font-medium transition-colors"
            :class="passwordCopied ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-white/[0.04] text-white/50 border border-white/[0.06] hover:border-white/[0.12] hover:text-white/70'"
          >
            {{ passwordCopied ? 'Copied to clipboard' : 'Copy Password' }}
          </button>
          <p class="text-[11px] text-white/30 mt-2 leading-relaxed">
            This is the password set in device settings for client access.
          </p>
        </div>
      </div>

      <!-- Go Home Button (primary - matches devices.vue) -->
      <button
        @click="navigateTo('/')"
        class="w-full px-4 py-2.5 bg-white text-black rounded-lg text-sm font-semibold text-center border border-dashed border-white/[0.12] hover:bg-transparent hover:text-white hover:border-white/[0.25] transition-colors"
      >
        Go to Home
      </button>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="flex flex-col items-center gap-6">
      <!-- Error Icon -->
      <div class="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center">
        <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>

      <div class="text-center">
        <h2 class="text-base font-semibold text-white/90 mb-1">Payment Error</h2>
        <p class="text-xs text-white/40">{{ errorMessage }}</p>
      </div>

      <!-- Go Home Button (secondary - matches devices.vue) -->
      <button
        @click="navigateTo('/')"
        class="px-8 py-2.5 bg-white/[0.06] text-white/80 rounded-lg text-sm font-medium tracking-wide border border-dashed border-white/[0.12] hover:border-white/[0.25] hover:bg-white/[0.1] transition-colors"
      >
        Go to Home
      </button>
    </div>
  </div>
</template>

<style scoped></style>
