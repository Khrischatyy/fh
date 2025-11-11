<template>
  <div>
    <NuxtLayout
      title="Device Management"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <div class="container mx-auto px-2 md:px-4">
        <!-- Header -->
        <div class="mb-6">
          <p class="text-neutral-400 text-sm">
            Devices are automatically registered when users sign in through the Mac OS app.
            Download the app, sign in with your studio owner account, and the device will appear here.
          </p>
          <a
            href="/downloads/FunnyHow-DeviceMonitor.dmg"
            class="inline-block mt-3 px-4 py-2 bg-white text-black rounded-lg hover:opacity-90"
            target="_blank"
          >
            📦 Download Mac OS App (Coming Soon)
          </a>
        </div>

        <!-- Devices Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <Spinner :is-loading="isLoading" />

          <!-- Empty State -->
          <div
            v-if="devices.length === 0 && !isLoading"
            class="col-span-full p-[10px] text-white rounded-[10px] h-full flex items-center justify-center border border-dashed border-white border-opacity-20"
          >
            <div class="flex flex-col justify-center text-center items-center m-10">
              <IconMonitor class="w-16 h-16 mb-4 opacity-50" />
              <span class="text-xl text-neutral-700">No devices registered yet</span>
              <span class="text-sm text-neutral-600 mt-2">
                Download the Mac OS app and sign in to automatically register your first device
              </span>
            </div>
          </div>

          <!-- Device Cards -->
          <DeviceCard
            v-for="device in devices"
            :key="device.id"
            :device="device"
            @onBlock="handleBlockDevice"
            @onUnblock="handleUnblockDevice"
            @onDelete="handleDeleteDevice"
            @onEdit="handleEditDevice"
          />
        </div>
      </div>

      <!-- Edit Device Modal -->
      <EditDeviceModal
        v-if="showEditModal && selectedDevice"
        :show-modal="showEditModal"
        :device="selectedDevice"
        @close="showEditModal = false"
        @updated="handleDeviceUpdated"
      />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useApi } from "~/src/lib/api"
import { Spinner, IconMonitor } from "~/src/shared/ui/common"
import DeviceCard from "~/src/entities/Device/ui/DeviceCard.vue"
import EditDeviceModal from "~/src/widgets/Modals/EditDeviceModal.vue"
import { useCookie, navigateTo } from "#app"
import { ACCESS_TOKEN_KEY } from "~/src/lib/api/config"
import { useSessionStore } from "~/src/entities/Session"
import { STUDIO_OWNER_ROLE } from "~/src/entities/Session"

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

const devices = ref<Device[]>([])
const isLoading = ref(true)
const showEditModal = ref(false)
const selectedDevice = ref<Device | null>(null)

onMounted(async () => {
  // Check authentication
  const token = useCookie(ACCESS_TOKEN_KEY).value
  if (!token) {
    await navigateTo('/login')
    return
  }

  // Check if user is studio owner
  const session = useSessionStore()
  if (session.userRole !== STUDIO_OWNER_ROLE) {
    await navigateTo('/')
    return
  }

  fetchDevices()
})

const fetchDevices = async () => {
  isLoading.value = true
  const { get: getDevices } = useApi({
    url: `/devices`,
    auth: true,
  })

  try {
    const response = await getDevices()
    devices.value = response.data
  } catch (error) {
    console.error("Error fetching devices:", error)
  } finally {
    isLoading.value = false
  }
}

const handleBlockDevice = async (deviceId: number) => {
  const { post: blockDevice } = useApi({
    url: `/devices/block`,
    auth: true,
  })

  try {
    await blockDevice({ device_id: deviceId, block: true })
    await fetchDevices()
  } catch (error) {
    console.error("Error blocking device:", error)
  }
}

const handleUnblockDevice = async (deviceId: number) => {
  const { post: unblockDevice } = useApi({
    url: `/devices/block`,
    auth: true,
  })

  try {
    await unblockDevice({ device_id: deviceId, block: false })
    await fetchDevices()
  } catch (error) {
    console.error("Error unblocking device:", error)
  }
}

const handleDeleteDevice = async (deviceId: number) => {
  if (!confirm("Are you sure you want to delete this device?")) {
    return
  }

  const { del: deleteDevice } = useApi({
    url: `/devices/${deviceId}`,
    auth: true,
  })

  try {
    await deleteDevice()
    await fetchDevices()
  } catch (error) {
    console.error("Error deleting device:", error)
  }
}

const handleEditDevice = (device: Device) => {
  selectedDevice.value = device
  showEditModal.value = true
}

const handleDeviceUpdated = () => {
  showEditModal.value = false
  selectedDevice.value = null
  fetchDevices()
}
</script>

<style scoped></style>
