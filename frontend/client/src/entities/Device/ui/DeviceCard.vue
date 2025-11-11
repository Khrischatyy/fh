<template>
  <div class="bg-black p-4 rounded-md shadow-lg flex flex-col gap-5 justify-between border border-white border-opacity-30">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div class="flex justify-start items-center gap-3">
        <div class="h-[35px] w-[35px] flex items-center justify-center bg-white bg-opacity-10 rounded">
          <IconMonitor class="w-6 h-6" />
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">
            {{ device.name }}
          </h3>
          <p :class="getStatusColor()" class="font-['Montserrat'] text-sm">
            {{ getStatusText() }}
          </p>
        </div>
      </div>
      <!-- Status Indicator -->
      <div :class="getStatusDotClass()" class="w-3 h-3 rounded-full"></div>
    </div>

    <!-- Device Info -->
    <div class="flex flex-col gap-3">
      <!-- MAC Address -->
      <div class="flex items-center gap-2">
        <IconAddress class="opacity-20" />
        <div class="flex flex-col">
          <span class="text-white opacity-20 text-xs">MAC Address</span>
          <span class="text-white text-sm font-mono">{{ device.mac_address }}</span>
        </div>
      </div>

      <!-- Last Heartbeat -->
      <div class="flex items-center gap-2">
        <IconClock class="opacity-20" />
        <div class="flex flex-col">
          <span class="text-white opacity-20 text-xs">Last Seen</span>
          <span class="text-white text-sm">{{ formatLastSeen() }}</span>
        </div>
      </div>

      <!-- OS Version -->
      <div v-if="device.os_version" class="flex items-center gap-2">
        <IconMonitor class="opacity-20" />
        <div class="flex flex-col">
          <span class="text-white opacity-20 text-xs">OS Version</span>
          <span class="text-white text-sm">{{ device.os_version }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-2">
      <button
        v-if="device.is_blocked"
        @click="$emit('onUnblock', device.id)"
        class="flex-1 h-10 hover:opacity-90 bg-green-600 rounded-[10px] text-white text-sm font-medium tracking-wide"
      >
        Unblock Device
      </button>
      <button
        v-else
        @click="$emit('onBlock', device.id)"
        class="flex-1 h-10 hover:opacity-90 bg-red-600 rounded-[10px] text-white text-sm font-medium tracking-wide"
      >
        Block Device
      </button>
      <button
        @click="$emit('onEdit', device)"
        class="h-10 px-4 hover:opacity-90 bg-white bg-opacity-10 rounded-[10px] text-white text-sm font-medium"
      >
        Edit
      </button>
      <button
        @click="$emit('onDelete', device.id)"
        class="h-10 px-4 hover:opacity-90 bg-red-600 bg-opacity-20 rounded-[10px] text-red-500 text-sm font-medium"
      >
        <IconTrash class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { IconMonitor, IconClock, IconTrash } from "~/src/shared/ui/common"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"

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

defineEmits<{
  (e: "onBlock", deviceId: number): void
  (e: "onUnblock", deviceId: number): void
  (e: "onDelete", deviceId: number): void
  (e: "onEdit", device: Device): void
}>()

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

const getStatusDotClass = () => {
  if (props.device.is_blocked) {
    return "bg-red-500"
  } else if (!props.device.is_active) {
    return "bg-neutral-500"
  } else {
    return "bg-green-500 animate-pulse"
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
</script>

<style scoped></style>
