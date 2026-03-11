<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta } from "#imports"
import { ref, computed, onMounted } from "vue"
import { useApi } from "~/src/lib/api"
import { navigateTo, useRoute } from "nuxt/app"
import { Spinner } from "~/src/shared/ui/common"

useHead({
  title: "Funny How – Device Payment",
  meta: [{ name: "description", content: "Pay for Device Time" }],
})
definePageMeta({
  layout: "error",
})

const route = useRoute()
const isLoading = ref(false)
const isLoadingDevice = ref(true)
const errorMessage = ref("")
const deviceUuid = computed(() => route.query.device_uuid as string)

interface DeviceInfo {
  name: string
  price_per_hour: number
  is_blocked: boolean
}

const deviceInfo = ref<DeviceInfo | null>(null)

const hoursOptions = computed(() => {
  const rate = deviceInfo.value?.price_per_hour || 25
  return [
    { value: 1, label: "1 hour", price: rate * 1 },
    { value: 2, label: "2 hours", price: rate * 2 },
    { value: 4, label: "4 hours", price: rate * 4 },
    { value: 8, label: "8 hours", price: rate * 8 },
    { value: 12, label: "12 hours", price: rate * 12 },
    { value: 24, label: "24 hours (1 day)", price: rate * 24 },
    { value: 48, label: "48 hours (2 days)", price: rate * 48 },
    { value: 168, label: "168 hours (1 week)", price: rate * 168 },
  ]
})

const selectedHours = ref(1)
const selectedPrice = computed(() => {
  const option = hoursOptions.value.find(opt => opt.value === selectedHours.value)
  return option?.price || (deviceInfo.value?.price_per_hour || 25)
})

const fetchDeviceInfo = async () => {
  if (!deviceUuid.value) {
    errorMessage.value = "Device UUID is missing"
    isLoadingDevice.value = false
    return
  }

  try {
    const { fetch: getInfo } = useApi({
      url: `/devices/info/${deviceUuid.value}`,
    })

    const response = await getInfo()
    if (response.success) {
      deviceInfo.value = {
        name: response.name,
        price_per_hour: response.price_per_hour,
        is_blocked: response.is_blocked,
      }
    } else {
      errorMessage.value = response.message || "Device not found"
    }
  } catch (error: any) {
    errorMessage.value = "Device not found"
  } finally {
    isLoadingDevice.value = false
  }
}

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
  fetchDeviceInfo()
})
</script>

<template>
  <div class="w-full max-w-md px-4">
    <Spinner :is-loading="isLoadingDevice" />

    <!-- Error State -->
    <div
      v-if="errorMessage && !isLoadingDevice"
      class="flex flex-col items-center gap-5 text-center"
    >
      <div class="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center">
        <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <div>
        <h1 class="text-base font-semibold text-white/90 mb-1">Device Not Found</h1>
        <p class="text-xs text-white/40">{{ errorMessage }}</p>
      </div>
      <button
        @click="navigateTo('/')"
        class="px-8 py-2.5 bg-white/[0.06] text-white/80 rounded-lg text-sm font-medium tracking-wide border border-dashed border-white/[0.12] hover:border-white/[0.25] hover:bg-white/[0.1] transition-colors"
      >
        Go to Home
      </button>
    </div>

    <!-- Payment Form -->
    <div v-if="deviceInfo && !isLoadingDevice && !errorMessage">
      <!-- Header -->
      <div class="mb-6 text-center">
        <div class="flex items-center justify-center gap-3 mb-3">
          <div class="w-8 h-8 rounded-full bg-white/[0.08] flex items-center justify-center">
            <svg class="w-4 h-4 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <h2 class="text-base font-semibold text-white/90 mb-1">Pay for Device Time</h2>
        <p class="text-xs text-white/40">{{ deviceInfo.name }}</p>
      </div>

      <div class="bg-neutral-900/60 border border-white/[0.06] rounded-[10px] p-5">
        <!-- Select Duration -->
        <div class="mb-5">
          <label class="block text-xs font-medium text-white/50 uppercase tracking-wider mb-2">Select Duration</label>
          <div class="relative">
            <select
              v-model.number="selectedHours"
              class="w-full px-4 py-2.5 bg-white/[0.06] border border-dashed border-white/[0.12] rounded-lg text-sm text-white/80 appearance-none cursor-pointer hover:border-white/[0.25] hover:bg-white/[0.1] focus:outline-none focus:border-white/[0.3] transition-colors"
            >
              <option
                v-for="option in hoursOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }} — ${{ option.price.toFixed(2) }}
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
              <svg class="w-4 h-4 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Price Summary -->
        <div class="bg-black/30 border border-white/[0.04] rounded-lg p-4 mb-5">
          <div class="flex justify-between items-center text-xs text-white/40 mb-2">
            <span>Duration</span>
            <span class="text-white/60">{{ hoursOptions.find(opt => opt.value === selectedHours)?.label }}</span>
          </div>
          <div class="flex justify-between items-center text-xs text-white/40 mb-2">
            <span>Rate</span>
            <span class="text-white/60">${{ deviceInfo.price_per_hour.toFixed(2) }}/hr</span>
          </div>
          <div class="border-t border-white/[0.06] mt-2 pt-2 flex justify-between items-center">
            <span class="text-sm font-semibold text-white/90">Total</span>
            <span class="text-sm font-semibold text-white">${{ selectedPrice.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Pay Button (primary - matches devices.vue Download .dmg) -->
        <button
          @click="createPaymentSession"
          :disabled="isLoading"
          class="w-full px-4 py-2.5 bg-white text-black rounded-lg text-sm font-semibold text-center border border-dashed border-white/[0.12] hover:bg-transparent hover:text-white hover:border-white/[0.25] transition-colors disabled:opacity-40 disabled:cursor-not-allowed mb-3"
        >
          {{ isLoading ? 'Processing...' : 'Continue to Payment' }}
        </button>

        <!-- Cancel Button (secondary - matches devices.vue Generate Token) -->
        <button
          @click="navigateTo('/')"
          class="w-full px-4 py-2.5 bg-white/[0.06] text-white/80 rounded-lg text-sm font-medium tracking-wide border border-dashed border-white/[0.12] hover:border-white/[0.25] hover:bg-white/[0.1] transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
select option {
  background-color: #171717;
  color: rgba(255, 255, 255, 0.8);
}
</style>
