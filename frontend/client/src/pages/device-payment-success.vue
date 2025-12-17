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
</style>
