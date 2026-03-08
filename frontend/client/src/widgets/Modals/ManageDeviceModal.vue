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
    return "text-red-400/70"
  } else if (!props.device.is_active) {
    return "text-neutral-500"
  } else {
    return "text-green-500/70"
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
  <div
    v-if="showPopup"
    class="fixed inset-0 flex items-center justify-center z-[1001] p-4"
  >
    <!-- Backdrop -->
    <div @click="closePopup" class="fixed inset-0 bg-black/60 z-10"></div>

    <!-- Modal -->
    <div class="bg-[#171717] rounded-[10px] w-full max-w-md p-5 relative z-20">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-white/[0.06] flex items-center justify-center">
            <IconMonitor class="w-5 h-5 text-white/60" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white leading-tight">{{ device?.name }}</h3>
            <div class="flex items-center gap-1.5 mt-0.5">
              <div v-if="device.is_active && !device.is_blocked" class="w-1.5 h-1.5 rounded-full bg-green-600/70"></div>
              <span :class="getStatusColor()" class="text-sm font-medium">{{ getStatusText() }}</span>
            </div>
          </div>
        </div>
        <button
          @click="closePopup"
          class="w-6 h-6 rounded-md hover:bg-white/[0.08] flex items-center justify-center"
        >
          <svg class="w-3 h-3 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Device Info -->
      <div class="mb-4">
        <div class="flex items-center justify-between py-2.5 border-b border-white/[0.06]">
          <span class="text-[11px] text-white/30 uppercase tracking-wider">MAC Address</span>
          <span class="text-xs text-white/70 font-mono">{{ device.mac_address }}</span>
        </div>
        <div class="flex items-center justify-between py-2.5 border-b border-white/[0.06]">
          <span class="text-[11px] text-white/30 uppercase tracking-wider">Last Seen</span>
          <span class="text-xs text-white/70">{{ formatLastSeen() }}</span>
        </div>
        <div v-if="device.os_version" class="flex items-center justify-between py-2.5 border-b border-white/[0.06]">
          <span class="text-[11px] text-white/30 uppercase tracking-wider">OS</span>
          <span class="text-xs text-white/70">{{ device.os_version }}</span>
        </div>
        <div class="flex items-center justify-between py-2.5">
          <span class="text-[11px] text-white/30 uppercase tracking-wider">IP</span>
          <span class="text-xs text-white/70">{{ device.last_ip || 'Unknown' }}</span>
        </div>
      </div>

      <!-- Device Name -->
      <div class="mb-5">
        <label class="text-[11px] text-white/30 uppercase tracking-wider block mb-1.5">Device Name</label>
        <input
          type="text"
          v-model="formData.name"
          placeholder="Enter device name"
          class="w-full px-3 h-11 outline-none rounded-[10px] border border-dashed border-white/[0.12] hover:border-white/[0.2] focus:border-white/40 bg-transparent text-white text-sm font-medium tracking-wide"
        />
      </div>

      <!-- Actions -->
      <div class="flex flex-col gap-2.5">
        <div class="flex gap-2.5">
          <button
            @click="handleBlockUnblock"
            class="flex-1 h-11 rounded-[10px] border border-dashed text-sm font-medium tracking-wide"
            :class="device.is_blocked ? 'border-green-600/50 bg-green-600/[0.04] hover:border-green-600/30 hover:bg-transparent text-green-500/70 transition-colors' : 'border-orange-500/50 bg-orange-500/[0.04] hover:border-orange-500/30 hover:bg-transparent text-orange-400/80 transition-colors'"
          >
            {{ device.is_blocked ? 'Unblock' : 'Block' }}
          </button>
          <button
            @click="handleSave"
            :disabled="isSaving"
            class="flex-1 h-11 rounded-[10px] border border-dashed border-white/[0.25] bg-white/[0.08] hover:border-white/[0.12] hover:bg-white/[0.04] text-white text-sm font-medium tracking-wide transition-colors disabled:opacity-50"
          >
            {{ isSaving ? 'Saving...' : 'Save' }}
          </button>
        </div>
        <button
          @click="handleDelete"
          class="w-full h-11 rounded-[10px] border border-dashed border-red-500/40 bg-red-500/[0.04] hover:border-red-500/20 hover:bg-transparent text-red-400/70 text-sm font-medium tracking-wide transition-colors"
        >
          Delete Device
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
