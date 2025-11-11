<script setup lang="ts">
import { Popup } from "~/src/shared/ui/components"
import { computed, reactive, ref, watch } from "vue"
import { FInputClassic } from "~/src/shared/ui/common"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common/Spinner"

interface Device {
  id: number
  name: string
  mac_address: string
  device_uuid: string
  is_blocked: boolean
  is_active: boolean
  last_heartbeat: string | null
  last_ip: string | null
  os_version: string | null
  app_version: string | null
  notes: string | null
  created_at: string
}

const props = withDefaults(
  defineProps<{
    showModal: boolean
    device: Device
  }>(),
  {
    showModal: false,
  }
)

const isLoading = ref(false)
const errorFromServer = ref("")

const deviceData = reactive({
  name: props.device.name,
  notes: props.device.notes || "",
  unlock_password: "",
  is_active: props.device.is_active,
})

watch(
  () => props.device,
  (newDevice) => {
    deviceData.name = newDevice.name
    deviceData.notes = newDevice.notes || ""
    deviceData.is_active = newDevice.is_active
  }
)

const emit = defineEmits<{
  (e: "close"): void
  (e: "updated"): void
}>()

const closeModal = () => {
  emit("close")
}

const isFormValid = computed(() => {
  return !!deviceData.name
})

const updateDevice = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  errorFromServer.value = ""

  const { patch: update } = useApi({
    url: `/devices/${props.device.id}`,
    auth: true,
  })

  try {
    const updateData: any = {
      name: deviceData.name,
      notes: deviceData.notes || null,
      is_active: deviceData.is_active,
    }

    if (deviceData.unlock_password) {
      updateData.unlock_password = deviceData.unlock_password
    }

    await update(updateData)
    emit("updated")
    emit("close")
  } catch (error: any) {
    errorFromServer.value = error?.response?.data?.message || "Failed to update device"
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <Popup :show-popup="showModal" @togglePopup="closeModal">
    <div
      :class="`border-white border-opacity-20 max-w-[600px]`"
      class="bg-black p-[30px] text-white rounded-[30px] flex flex-col gap-5 border"
    >
      <div class="flex justify-between">
        <h2 class="text-2xl font-bold">Edit Device</h2>
        <button @click="closeModal" class="text-white hover:opacity-70">✕</button>
      </div>

      <div class="flex flex-col gap-4">
        <!-- Device Info (Read-only) -->
        <div class="bg-neutral-900 p-4 rounded-lg">
          <div class="flex flex-col gap-2 text-sm">
            <div>
              <span class="text-neutral-400">MAC Address:</span>
              <span class="text-white ml-2 font-mono">{{ device.mac_address }}</span>
            </div>
            <div>
              <span class="text-neutral-400">Device UUID:</span>
              <span class="text-white ml-2 font-mono">{{ device.device_uuid }}</span>
            </div>
            <div v-if="device.os_version">
              <span class="text-neutral-400">OS Version:</span>
              <span class="text-white ml-2">{{ device.os_version }}</span>
            </div>
            <div v-if="device.app_version">
              <span class="text-neutral-400">App Version:</span>
              <span class="text-white ml-2">{{ device.app_version }}</span>
            </div>
          </div>
        </div>

        <!-- Editable Fields -->
        <FInputClassic
          v-model="deviceData.name"
          label="Device Name"
          placeholder="e.g., Studio Mac #1"
        />

        <div class="flex flex-col gap-2">
          <label class="text-sm text-neutral-400">Notes</label>
          <textarea
            v-model="deviceData.notes"
            placeholder="Add notes about this device..."
            class="bg-neutral-900 text-white px-4 py-3 rounded-lg min-h-[100px] resize-none focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-20"
          />
        </div>

        <FInputClassic
          v-model="deviceData.unlock_password"
          type="password"
          label="Update Unlock Password (optional)"
          placeholder="Leave blank to keep current password"
        />

        <div class="flex items-center gap-3">
          <input
            type="checkbox"
            id="is_active"
            v-model="deviceData.is_active"
            class="w-5 h-5 rounded"
          />
          <label for="is_active" class="text-sm text-white">
            Device is active
          </label>
        </div>

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
            @click="updateDevice"
            :disabled="!isFormValid || isLoading"
            class="flex-1 h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Spinner v-if="isLoading" :is-loading="isLoading" />
            <span v-else>Save Changes</span>
          </button>
        </div>
      </div>
    </div>
  </Popup>
</template>

<style scoped></style>
