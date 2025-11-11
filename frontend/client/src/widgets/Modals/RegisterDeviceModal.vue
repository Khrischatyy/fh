<script setup lang="ts">
import { Popup } from "~/src/shared/ui/components"
import { computed, reactive, ref } from "vue"
import { FInputClassic } from "~/src/shared/ui/common"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common/Spinner"

const props = withDefaults(
  defineProps<{
    showModal: boolean
  }>(),
  {
    showModal: false,
  }
)

const isLoading = ref(false)
const errorFromServer = ref("")
const registeredToken = ref("")

const device = reactive({
  name: "",
  mac_address: "",
  device_uuid: "",
  os_version: "",
  app_version: "",
  unlock_password: "",
})

const emit = defineEmits<{
  (e: "close"): void
  (e: "registered"): void
}>()

const closeModal = () => {
  emit("close")
}

const isFormValid = computed(() => {
  return !!device.name && !!device.mac_address && !!device.device_uuid
})

const showError = (field: string) => {
  return !device[field] ? `Field is required` : ""
}

const registerDevice = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  errorFromServer.value = ""

  const { post: register } = useApi({
    url: `/devices/register`,
    auth: true,
  })

  try {
    const response = await register(device)
    registeredToken.value = response.device_token
    // Show token to user - they need to save it
  } catch (error: any) {
    errorFromServer.value = error?.response?.data?.message || "Failed to register device"
    isLoading.value = false
  }
}

const copyToken = () => {
  navigator.clipboard.writeText(registeredToken.value)
  alert("Device token copied to clipboard!")
}

const finishRegistration = () => {
  emit("registered")
  emit("close")
}
</script>

<template>
  <Popup :show-popup="showModal" @togglePopup="closeModal">
    <div
      :class="`border-white border-opacity-20 max-w-[600px]`"
      class="bg-black p-[30px] text-white rounded-[30px] flex flex-col gap-5 border"
    >
      <div class="flex justify-between">
        <h2 class="text-2xl font-bold">
          {{ registeredToken ? "Device Registered!" : "Register Device" }}
        </h2>
        <button @click="closeModal" class="text-white hover:opacity-70">✕</button>
      </div>

      <!-- Registration Success - Show Token -->
      <div v-if="registeredToken" class="flex flex-col gap-4">
        <p class="text-neutral-400">
          Device registered successfully! Save this token securely - you'll need it for the Mac OS app.
        </p>

        <div class="bg-neutral-900 p-4 rounded-lg">
          <label class="text-sm text-neutral-400 mb-2 block">Device Token</label>
          <div class="flex gap-2">
            <input
              :value="registeredToken"
              readonly
              class="flex-1 bg-neutral-800 text-white px-4 py-2 rounded-lg font-mono text-sm"
            />
            <button
              @click="copyToken"
              class="px-4 py-2 bg-white text-black rounded-lg hover:opacity-90"
            >
              Copy
            </button>
          </div>
        </div>

        <p class="text-yellow-500 text-sm">
          ⚠️ Save this token now! You won't be able to see it again.
        </p>

        <button
          @click="finishRegistration"
          class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
        >
          Done
        </button>
      </div>

      <!-- Registration Form -->
      <div v-else class="flex flex-col gap-4">
        <p class="text-neutral-400 text-sm">
          Register a Mac OS device that will be monitored and can be blocked remotely.
        </p>

        <FInputClassic
          v-model="device.name"
          label="Device Name"
          placeholder="e.g., Studio Mac #1"
          :error="showError('name')"
        />

        <FInputClassic
          v-model="device.mac_address"
          label="MAC Address"
          placeholder="e.g., 00:1B:63:84:45:E6"
          :error="showError('mac_address')"
        />

        <FInputClassic
          v-model="device.device_uuid"
          label="Device UUID"
          placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000"
          :error="showError('device_uuid')"
        />

        <FInputClassic
          v-model="device.os_version"
          label="OS Version (optional)"
          placeholder="e.g., macOS 14.0"
        />

        <FInputClassic
          v-model="device.app_version"
          label="App Version (optional)"
          placeholder="e.g., 1.0.0"
        />

        <FInputClassic
          v-model="device.unlock_password"
          type="password"
          label="Unlock Password (optional)"
          placeholder="Set a password to unlock device locally"
        />

        <div v-if="errorFromServer" class="text-red-500 text-sm">
          {{ errorFromServer }}
        </div>

        <div class="flex gap-3">
          <button
            @click="closeModal"
            class="flex-1 h-11 hover:opacity-90 bg-neutral-800 rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            Cancel
          </button>
          <button
            @click="registerDevice"
            :disabled="!isFormValid || isLoading"
            class="flex-1 h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Spinner v-if="isLoading" :is-loading="isLoading" />
            <span v-else>Register Device</span>
          </button>
        </div>
      </div>
    </div>
  </Popup>
</template>

<style scoped></style>
