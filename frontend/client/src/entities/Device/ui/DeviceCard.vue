<template>
  <div class="bg-neutral-900/60 border border-white/[0.06] rounded-[10px] p-5 flex flex-col justify-between">
    <!-- Header -->
    <div>
      <div class="flex items-start justify-between mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-white/[0.06] flex items-center justify-center">
            <IconMonitor class="w-5 h-5 text-white/60" />
          </div>
          <div>
            <h3 class="text-base font-semibold text-white leading-tight">{{ device.name }}</h3>
            <div class="flex items-center gap-1.5 mt-0.5">
              <div :class="getStatusDotClass()" class="w-1.5 h-1.5 rounded-full"></div>
              <span :class="getStatusColor()" class="text-sm font-medium">{{ getStatusText() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Info Grid -->
      <div class="space-y-2.5 mb-5">
        <div class="flex items-center justify-between py-2 border-b border-white/[0.04]">
          <span class="text-[11px] text-white/30 uppercase tracking-wider">MAC</span>
          <span class="text-xs text-white/70 font-mono">{{ device.mac_address }}</span>
        </div>
        <div class="flex items-center justify-between py-2 border-b border-white/[0.04]">
          <span class="text-[11px] text-white/30 uppercase tracking-wider">Last Seen</span>
          <span class="text-xs text-white/70">{{ formatLastSeen() }}</span>
        </div>
        <div v-if="device.os_version" class="flex items-center justify-between py-2">
          <span class="text-[11px] text-white/30 uppercase tracking-wider">OS</span>
          <span class="text-xs text-white/70">{{ device.os_version }}</span>
        </div>
      </div>
    </div>

    <!-- Manage Button -->
    <button
      @click.stop="manageDevicePopup"
      class="w-full py-2.5 bg-white/[0.06] border border-dashed border-white/[0.12] rounded-lg text-white/80 text-xs font-semibold tracking-wide"
    >
      Manage Device
    </button>
  </div>
</template>

<script setup lang="ts">
import { IconMonitor } from "~/src/shared/ui/common"

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

const props = defineProps<{
  device: Device
}>()

const emit = defineEmits<{
  (e: "manageDevice", device: Device): void
}>()

const manageDevicePopup = () => {
  emit("manageDevice", props.device)
}

const getStatusText = () => {
  if (props.device.is_blocked) return "Blocked"
  if (!props.device.is_active) return "Inactive"
  return "Active"
}

const getStatusColor = () => {
  if (props.device.is_blocked) return "text-red-500"
  if (!props.device.is_active) return "text-neutral-500"
  return "text-green-500/70"
}

const getStatusDotClass = () => {
  if (props.device.is_blocked) return "bg-red-500"
  if (!props.device.is_active) return "bg-neutral-500"
  return "bg-green-600/70"
}

const formatLastSeen = () => {
  if (!props.device.last_heartbeat) return "Never"

  const lastSeen = new Date(props.device.last_heartbeat)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - lastSeen.getTime()) / 60000)

  if (diffMins < 1) return "Just now"
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`
  if (diffMins < 1440) {
    const h = Math.floor(diffMins / 60)
    return `${h} hour${h > 1 ? "s" : ""} ago`
  }
  const d = Math.floor(diffMins / 1440)
  return `${d} day${d > 1 ? "s" : ""} ago`
}
</script>
