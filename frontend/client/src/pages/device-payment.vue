<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta } from "#imports"
import { ref, computed, onMounted } from "vue"
import { useApi } from "~/src/lib/api"
import { navigateTo, useRoute } from "nuxt/app"
import { Spinner } from "~/src/shared/ui/common"

// Meta tags for the page
useHead({
  title: "Funny How – Device Payment",
  meta: [{ name: "description", content: "Pay for Device Time" }],
})
definePageMeta({
  layout: "main",
})

const route = useRoute()
const isLoading = ref(false)
const errorMessage = ref("")
const deviceUuid = computed(() => route.query.device_uuid as string)
const deviceName = computed(() => route.query.device_name as string || "Device")

// Hours options (1-48 hours)
const hoursOptions = [
  { value: 1, label: "1 hour", price: 25 },
  { value: 2, label: "2 hours", price: 50 },
  { value: 4, label: "4 hours", price: 100 },
  { value: 8, label: "8 hours", price: 200 },
  { value: 12, label: "12 hours", price: 300 },
  { value: 24, label: "24 hours (1 day)", price: 600 },
  { value: 48, label: "48 hours (2 days)", price: 1200 },
  { value: 168, label: "168 hours (1 week)", price: 4200 },
]

const selectedHours = ref(1)
const selectedPrice = computed(() => {
  const option = hoursOptions.find(opt => opt.value === selectedHours.value)
  return option?.price || 25
})

const createPaymentSession = async () => {
  if (!deviceUuid.value) {
    errorMessage.value = "Device UUID is missing"
    return
  }

  isLoading.value = true
  errorMessage.value = ""

  try {
    const { post: createSession } = useApi({
      url: "/devices/create-payment-session",
    })

    const response = await createSession({
      device_uuid: deviceUuid.value,
      unlock_duration_hours: selectedHours.value,
    })

    if (response.success && response.payment_url) {
      // Redirect to Stripe checkout
      window.location.href = response.payment_url
    } else {
      errorMessage.value = response.message || "Failed to create payment session"
    }
  } catch (error: any) {
    errorMessage.value = error.message || "Failed to create payment session"
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (!deviceUuid.value) {
    errorMessage.value = "Device UUID is missing"
  }
})
</script>

<template>
  <div class="container">
    <Spinner :is-loading="isLoading" />

    <div v-if="!isLoading" class="payment-container">
      <h1 class="text-4xl font-bold mb-2">Pay for Device Time</h1>
      <p class="text-xl text-white/60 mb-8">{{ deviceName }}</p>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div v-else class="form-container">
        <div class="form-group">
          <label class="label">Select Duration</label>
          <select v-model.number="selectedHours" class="select-input">
            <option
              v-for="option in hoursOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }} - ${{ option.price.toFixed(2) }}
            </option>
          </select>
        </div>

        <div class="price-summary">
          <div class="price-row">
            <span>Duration:</span>
            <span>{{ hoursOptions.find(opt => opt.value === selectedHours)?.label }}</span>
          </div>
          <div class="price-row total">
            <span>Total:</span>
            <span>${{ selectedPrice.toFixed(2) }}</span>
          </div>
        </div>

        <button
          @click="createPaymentSession"
          :disabled="isLoading"
          class="pay-button"
        >
          Continue to Payment
        </button>

        <button
          @click="navigateTo('/')"
          class="cancel-button"
        >
          Cancel
        </button>
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
  padding: 2rem;
  background-color: #000;
  color: #fff;
}

.payment-container {
  max-width: 500px;
  width: 100%;
}

.error-message {
  padding: 1rem;
  background-color: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 10px;
  color: #dc2626;
  margin-bottom: 1rem;
}

.form-container {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 2rem;
}

.form-group {
  margin-bottom: 2rem;
}

.label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.select-input {
  width: 100%;
  padding: 0.75rem;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;

  &:hover {
    background-color: rgba(255, 255, 255, 0.15);
  }

  &:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.4);
  }

  option {
    background-color: #1a1a1a;
    color: #fff;
  }
}

.price-summary {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  color: rgba(255, 255, 255, 0.8);

  &.total {
    margin-top: 0.5rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 1.25rem;
    font-weight: 600;
    color: #fff;
  }
}

.pay-button {
  width: 100%;
  padding: 0.875rem 1.5rem;
  background-color: #fff;
  color: #000;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.025em;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-bottom: 0.75rem;

  &:hover:not(:disabled) {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.cancel-button {
  width: 100%;
  padding: 0.875rem 1.5rem;
  background-color: transparent;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.025em;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.3);
  }
}
</style>
