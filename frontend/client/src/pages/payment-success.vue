<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta, useRuntimeConfig } from "#imports"
import axios from "axios"
import { ref, onMounted, computed } from "vue"
import { useApi } from "~/src/lib/api"
import { navigateTo, useRoute } from "nuxt/app"
import { Spinner } from "~/src/shared/ui/common"

// Meta tags for the page
useHead({
  title: "Funny How – Payment Success",
  meta: [{ name: "description", content: "Processing Payment" }],
})
definePageMeta({
  layout: "error",
})

const route = useRoute()
const isLoading = ref(true)
const errorMessage = ref("")
const sessionId = computed(() => route.query.session_id)
const bookingId = computed(() => route.query.booking_id)
const order_id = computed(() => route.query.order_id)
const processPayment = async () => {
  const { post: paymentSuccess } = useApi({
    url: "/address/payment-success",
    // auth: true,
  })

  if (!bookingId.value) {
    errorMessage.value = "Invalid request parameters"
    isLoading.value = false
    return
  }

  paymentSuccess({
    session_id: sessionId.value,
    booking_id: bookingId.value,
  })
    .then((response) => {
      if (response.success) {
        // Payment successful, redirect to bookings
        navigateTo(response.redirect_url || "/bookings")
      } else {
        // Payment failed or error occurred
        errorMessage.value = response.message || "Payment verification failed."
      }
    })
    .catch((error) => {
      errorMessage.value = error.message?.error || error.message || "Payment verification failed."
    })
    .finally(() => {
      isLoading.value = false
    })
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
      <div v-else-if="errorMessage" class="flex flex-col gap-5">
        <div class="text-center">
          <h1 class="text-5xl font-bold">Error</h1>
          <p class="text-xl">{{ errorMessage }}</p>
        </div>
        <div class="flex justify-center items-center gap-2.5">
          <button
            @click="navigateTo('/bookings')"
            class="max-w-96 px-10 h-11 p-3.5 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            Go To My Bookings
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
</style>
