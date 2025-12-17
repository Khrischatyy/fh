<script setup lang="ts">
import { Popup } from "~/src/shared/ui/components"
import { computed, ref, watch } from "vue"
import { IconMonitor, IconClock } from "~/src/shared/ui/common"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common/Spinner"
import FInputClassic from "~/src/shared/ui/common/Input/FInputClassic.vue"

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
  current_password: string | null
  password_changed_at: string | null
  created_at: string
}

const props = withDefaults(
  defineProps<{
    showPopup: boolean
    device: Device
  }>(),
  {
    showPopup: false,
  },
)

const isLoading = ref(false)
const isSaving = ref(false)

const formData = ref({
  name: '',
  current_password: '',
})

const showPassword = ref(false)
const passwordCopied = ref(false)

const generatePassword = () => {
  const length = 12
  const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
  let password = ""
  for (let i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length))
  }
  formData.value.current_password = password
}

const copyPassword = async () => {
  if (formData.value.current_password) {
    await navigator.clipboard.writeText(formData.value.current_password)
    passwordCopied.value = true
    setTimeout(() => {
      passwordCopied.value = false
    }, 2000)
  }
}

const emit = defineEmits<{
  (e: "togglePopup"): void
  (e: "closePopup"): void
  (e: "onDeleteDevice", deviceId: number): void
  (e: "onBlockDevice", deviceId: number): void
  (e: "onUnblockDevice", deviceId: number): void
  (e: "updated"): void
}>()

const closePopup = () => {
  emit("closePopup")
}

const handleSave = async () => {
  isSaving.value = true

  try {
    const { patch: updateDevice } = useApi({
      url: `devices/${props.device?.id}`,
      auth: true,
    })

    const dataToSend = {
      name: formData.value.name,
      current_password: formData.value.current_password || null,
    }

    const response = await updateDevice(dataToSend)

    if (response.success) {
      emit('updated')
      closePopup()
    }
  } catch (error) {
    console.error('Failed to update device:', error)
    alert('Failed to update device. Please try again.')
  } finally {
    isSaving.value = false
  }
}

const handleBlockUnblock = () => {
  if (props.device.is_blocked) {
    emit('onUnblockDevice', props.device.id)
  } else {
    emit('onBlockDevice', props.device.id)
  }
}

const handleDelete = () => {
  if (confirm('Are you sure you want to delete this device?')) {
    emit('onDeleteDevice', props.device.id)
  }
}

const getStatusText = () => {
  if (props.device.is_blocked) {
    return "Blocked"
  } else if (!props.device.is_active) {
    return "Inactive"
  } else {
    return "Active"
  }
}

const getStatusColor = () => {
  if (props.device.is_blocked) {
    return "text-red-500"
  } else if (!props.device.is_active) {
    return "text-neutral-500"
  } else {
    return "text-green-500"
  }
}

const formatLastSeen = () => {
  if (!props.device.last_heartbeat) {
    return "Never"
  }

  const lastSeen = new Date(props.device.last_heartbeat)
  const now = new Date()
  const diffMs = now.getTime() - lastSeen.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) {
    return "Just now"
  } else if (diffMins < 60) {
    return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`
  } else if (diffMins < 1440) {
    const diffHours = Math.floor(diffMins / 60)
    return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`
  } else {
    const diffDays = Math.floor(diffMins / 1440)
    return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`
  }
}

// Watch for device changes and populate form
watch(() => props.device, (newDevice) => {
  if (newDevice && props.showPopup) {
    formData.value = {
      name: newDevice.name || '',
      current_password: newDevice.current_password || '',
    }
  }
}, { immediate: true })
</script>

<template>
  <Popup
    :scroll-to-close="true"
    type="small"
    :title="'Manage Device'"
    :open="showPopup"
    @close="closePopup"
  >
    <template #header>
      <div class="flex justify-start items-center gap-4">
        <div class="h-[35px] w-[35px] flex items-center justify-center bg-white bg-opacity-10 rounded">
          <IconMonitor class="w-6 h-6" />
        </div>
        <div>
          <h3 class="text-xl font-bold text-white mb-1">
            {{ device?.name }}
          </h3>
          <p
            :class="getStatusColor()"
            class="font-['Montserrat'] text-sm"
          >
            {{ getStatusText() }}
          </p>
        </div>
      </div>
    </template>
    <template #body>
      <div class="flex flex-col gap-6 justify-between items-center relative">
        <Spinner :is-loading="isLoading" />

        <!-- Device Info (Read-only) -->
        <div class="w-full bg-neutral-900 p-4 rounded-lg">
          <div class="flex flex-col gap-4 text-sm">
            <div class="flex items-center gap-2 pb-4">
              <IconAddress class="opacity-20" />
              <div class="flex flex-col gap-0.5">
                <span class="text-white opacity-20 text-xs">MAC Address</span>
                <span class="text-white text-sm font-mono">{{ device.mac_address }}</span>
              </div>
            </div>

            <div class="flex items-center gap-2 pb-4">
              <IconClock class="opacity-20" />
              <div class="flex flex-col gap-0.5">
                <span class="text-white opacity-20 text-xs">Last Seen</span>
                <span class="text-white text-sm">{{ formatLastSeen() }}</span>
              </div>
            </div>

            <div v-if="device.os_version" class="flex items-center gap-2 pb-4">
              <IconMonitor class="opacity-20" />
              <div class="flex flex-col gap-0.5">
                <span class="text-white opacity-20 text-xs">OS Version</span>
                <span class="text-white text-sm">{{ device.os_version }}</span>
              </div>
            </div>

            <div class="flex items-center">
              <IconMonitor class="opacity-20" />
              <div class="flex flex-col gap-0.5">
                <span class="text-white opacity-20 text-xs">Device UUID</span>
                <span class="text-white font-mono text-xs break-all">{{ device.device_uuid }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Editable Fields -->
        <div class="w-full flex flex-col ">
          <!-- Device Name -->
          <div class="pl-4 pr-4">
            <label class="text-white opacity-20 text-sm font-normal tracking-wide">Device Name</label>
            <FInputClassic
              :wide="true"
              type="text"
              v-model="formData.name"
              placeholder="Enter device name"
            />
          </div>

          <!-- Device Password -->
<!--          <div>-->
<!--            <label class="text-white opacity-20 text-sm font-normal tracking-wide">Device Password</label>-->
<!--            <div class="flex gap-2">-->
<!--              <div class="relative flex-1">-->
<!--                <FInputClassic-->
<!--                  :wide="true"-->
<!--                  :type="showPassword ? 'text' : 'password'"-->
<!--                  v-model="formData.current_password"-->
<!--                  placeholder="Enter or generate password"-->
<!--                  class="pr-20"-->
<!--                />-->
<!--                <button-->
<!--                  @click="showPassword = !showPassword"-->
<!--                  type="button"-->
<!--                  class="absolute right-3 top-1/2 -translate-y-1/2 text-white opacity-40 hover:opacity-100 text-xs"-->
<!--                >-->
<!--                  {{ showPassword ? 'Hide' : 'Show' }}-->
<!--                </button>-->
<!--              </div>-->
<!--              <button-->
<!--                @click="generatePassword"-->
<!--                type="button"-->
<!--                class="px-4 py-2 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-[10px] text-white text-sm font-medium tracking-wide whitespace-nowrap"-->
<!--              >-->
<!--                Generate-->
<!--              </button>-->
<!--              <button-->
<!--                v-if="formData.current_password"-->
<!--                @click="copyPassword"-->
<!--                type="button"-->
<!--                class="px-4 py-2 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-[10px] text-white text-sm font-medium tracking-wide"-->
<!--                :class="passwordCopied ? 'bg-green-700' : ''"-->
<!--              >-->
<!--                {{ passwordCopied ? '✓' : 'Copy' }}-->
<!--              </button>-->
<!--            </div>-->
<!--          </div>-->
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex flex-col gap-3 w-full">
        <div class="flex justify-between items-center gap-3 w-full">
          <button
            @click="handleBlockUnblock"
            :class="device.is_blocked ? 'bg-green-700 hover:bg-green-800 border-green-700' : 'bg-transparent border-red'"
            class="flex-1 h-11 p-3.5 hover:opacity-90 rounded-[10px] text-white border text-sm font-medium tracking-wide"
          >
            {{ device.is_blocked ? 'Unblock Device' : 'Block Device' }}
          </button>
          <button
            @click="handleSave"
            :disabled="isSaving"
            class="flex-1 h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-black text-sm font-medium tracking-wide disabled:opacity-50"
          >
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
        <button
          @click="handleDelete"
          class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-red border-red border text-sm font-medium tracking-wide"
        >
          Delete Device
        </button>
      </div>
    </template>
  </Popup>
</template>

<style scoped lang="scss"></style>
