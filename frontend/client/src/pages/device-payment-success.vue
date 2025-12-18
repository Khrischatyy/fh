<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta } from "#imports"
import { ref, onMounted, computed } from "vue"
import { useApi } from "~/src/lib/api"
import { navigateTo, useRoute } from "nuxt/app"
import { Spinner } from "~/src/shared/ui/common"

// Meta tags for the page
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
const showPasswordInfo = ref(false)

const sessionId = computed(() => route.query.session_id as string)
const deviceUuid = computed(() => route.query.device_uuid as string)

const processPayment = async () => {
  if (!sessionId.value || !deviceUuid.value) {
    errorMessage.value = "Invalid request parameters"
    isLoading.value = false
    return
  }

  try {
    const { get: paymentSuccess } = useApi({
      url: `/devices/payment-success?session_id=${sessionId.value}&device_uuid=${deviceUuid.value}`,
    })

    const response = await paymentSuccess()

    if (response.success) {
      successMessage.value = response.message || "Device unlocked successfully!"

      // Format expires_at for display
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

      // Store device info and password
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
  <div>
    <Spinner :is-loading="isLoading" />
    <div class="error flex flex-col gap-10">
      <div v-if="isLoading" class="text-center">
        <h1 class="text-5xl font-bold">Processing Payment...</h1>
      </div>

      <!-- Success State -->
      <div v-else-if="successMessage && !errorMessage" class="flex flex-col gap-5">
        <div class="text-center">
          <div class="success-icon">✓</div>
          <h1 class="text-5xl font-bold mb-4">Payment Successful!</h1>
          <p class="text-xl text-white/80 mb-2">{{ successMessage }}</p>
          <div v-if="expiresAt" class="expires-info">
            <p class="text-white/60">Your device is unlocked until:</p>
            <p class="text-2xl font-semibold text-white mt-2">{{ expiresAt }}</p>
          </div>

          <!-- Device Password Display -->
          <div v-if="devicePassword" class="password-info">
            <div class="password-header">
              <p class="text-white/60 text-sm">Device Password:</p>
              <button
                @click="showPasswordInfo = !showPasswordInfo"
                class="info-button"
                title="Click for more info"
              >
                ℹ
              </button>
            </div>
            <p class="text-3xl font-bold text-white mt-2 font-mono password-text">{{ devicePassword }}</p>
            <p v-if="deviceName" class="text-white/50 text-xs mt-2">{{ deviceName }}</p>

            <!-- Explanatory notification -->
            <div v-if="showPasswordInfo" class="password-explanation">
              <p class="text-sm text-white/80">
                💡 This is the password you set in the device modal. It won't change anything on your computer -
                it's just for showing the client the password from the computer if they don't know it.
              </p>
            </div>
          </div>
        </div>
        <div class="flex justify-center items-center gap-2.5">
          <button
            @click="navigateTo('/')"
            class="max-w-96 px-10 h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-black text-sm font-medium tracking-wide"
          >
            Go to Home
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="errorMessage" class="flex flex-col gap-5">
        <div class="text-center">
          <div class="error-icon">✗</div>
          <h1 class="text-5xl font-bold mb-4">Payment Error</h1>
          <p class="text-xl text-white/80">{{ errorMessage }}</p>
        </div>
        <div class="flex justify-center items-center gap-2.5">
          <button
            @click="navigateTo('/')"
            class="max-w-96 px-10 h-11 p-3.5 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            Go to Home
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #000;
  color: #fff;
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(34, 197, 94, 0.1);
  border: 2px solid rgba(34, 197, 94, 0.3);
  border-radius: 50%;
  font-size: 3rem;
  color: #22c55e;
}

.error-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(220, 38, 38, 0.1);
  border: 2px solid rgba(220, 38, 38, 0.3);
  border-radius: 50%;
  font-size: 3rem;
  color: #dc2626;
}

.expires-info {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  display: inline-block;
}

.password-info {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: rgba(59, 130, 246, 0.1);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  display: inline-block;
  min-width: 400px;
}

.password-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.info-button {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.info-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.password-text {
  letter-spacing: 0.05em;
  user-select: all;
  cursor: text;
}

.password-explanation {
  margin-top: 1rem;
  padding: 1rem;
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border-left: 3px solid rgba(59, 130, 246, 0.5);
  text-align: left;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
