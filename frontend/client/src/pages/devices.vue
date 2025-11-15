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
          <!-- Compact Info Card -->
          <div class="bg-gradient-to-br from-neutral-900 to-black border border-white border-opacity-20 rounded-2xl p-6 mb-6 shadow-xl">
            <div class="flex items-start justify-between gap-6 flex-wrap">
              <!-- Left Side - Info -->
              <div class="flex-1 min-w-[280px]">
                <div class="flex items-center gap-3 mb-3">
                  <h3 class="text-xl font-bold text-white">Register Device</h3>
                </div>
                <p class="text-neutral-400 text-sm mb-4 leading-relaxed">
                  Generate a secure one-time token to register your Mac device without entering passwords.
                </p>
                <div class="flex flex-wrap gap-2 text-xs text-neutral-500">
                  <span class="bg-neutral-800 px-2 py-1 rounded">Step 1: Generate</span>
                  <span class="bg-neutral-800 px-2 py-1 rounded">Step 2: Copy</span>
                  <span class="bg-neutral-800 px-2 py-1 rounded">Step 3: Register</span>
                </div>
              </div>

              <!-- Right Side - Actions -->
              <div class="flex flex-col gap-3 min-w-[200px]">
                <button
                  @click="generateToken"
                  :disabled="isGeneratingToken"
                  class="px-6 py-3 bg-white text-black rounded-lg hover:opacity-90 disabled:opacity-50 font-medium transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <span>{{ isGeneratingToken ? 'Generating...' : 'Generate Token' }}</span>
                </button>
                <a
                  href="/api/downloads/FunnyHow-DeviceMonitor.dmg"
                  class="px-6 py-3 bg-neutral-800 text-white rounded-lg hover:bg-neutral-700 transition-all font-medium flex items-center justify-center gap-2 border border-neutral-700"
                  download="FunnyHow-DeviceMonitor.dmg"
                >
                  <span>Download App</span>
                </a>
              </div>
            </div>
          </div>
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
            @manage-device="openDeviceModal"
          />
        </div>
      </div>

      <!-- Manage Device Modal -->
      <ManageDeviceModal
        v-if="showManageModal && selectedDevice"
        :showPopup="showManageModal"
        :device="selectedDevice"
        @closePopup="closeManageModal"
        @updated="handleDeviceUpdated"
        @on-delete-device="handleDeleteDevice"
        @on-block-device="handleBlockDevice"
        @on-unblock-device="handleUnblockDevice"
      />

      <!-- Token Display Modal -->
      <div
        v-if="showTokenModal"
        class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
        @click.self="showTokenModal = false"
      >
        <div class="bg-neutral-900 rounded-lg p-6 max-w-lg w-full border border-neutral-800">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold text-white">Token Generated</h2>
            <button
              @click="showTokenModal = false"
              class="text-neutral-400 hover:text-white transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <p class="text-neutral-400 text-sm mb-4">
            Copy this token and paste it in your Mac OS app
          </p>

          <div class="bg-neutral-800 bg-opacity-40 border border-neutral-600 rounded-lg p-3 mb-3">
            <p class="text-neutral-300 text-xs font-medium mb-2">Important:</p>
            <ul class="text-neutral-400 text-xs space-y-1">
              <li>• Expires in 24 hours</li>
              <li>• Single-use only</li>
              <li>• Keep secure</li>
            </ul>
          </div>

          <div class="bg-neutral-950 border border-neutral-700 rounded-lg p-3 mb-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-neutral-400 text-xs font-mono">TOKEN</span>
              <button
                @click="copyToken"
                class="px-3 py-1 bg-white text-black text-xs rounded hover:opacity-90 transition-opacity font-medium"
              >
                {{ tokenCopied ? 'Copied!' : 'Copy' }}
              </button>
            </div>
            <code class="text-white font-mono text-xs break-all block">{{ generatedToken }}</code>
          </div>

          <div class="space-y-2">
            <p class="text-white font-medium text-sm">How to use:</p>
            <ol class="text-neutral-300 text-xs space-y-1 ml-4">
              <li>1. Open FunnyHow Device Locker on your Mac</li>
              <li>2. Click menu bar icon and select "Register with Token..."</li>
              <li>3. Paste this token when prompted</li>
            </ol>
          </div>

          <p class="text-neutral-500 text-xs text-center mt-4">
            Expires: {{ tokenExpiresAt }}
          </p>
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useApi } from "~/src/lib/api"
import { Spinner, IconMonitor } from "~/src/shared/ui/common"
import DeviceCard from "~/src/entities/Device/ui/DeviceCard.vue"
import ManageDeviceModal from "~/src/widgets/Modals/ManageDeviceModal.vue"
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
const showManageModal = ref(false)
const selectedDevice = ref<Device | null>(null)

// Token generation state
const showTokenModal = ref(false)
const generatedToken = ref('')
const tokenCopied = ref(false)
const isGeneratingToken = ref(false)
const tokenExpiresAt = ref('')

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
  const { fetch: getDevices } = useApi({
    url: `/devices`,
    auth: true,
  })

  try {
    const response = await getDevices()
    if (response.success && response.data) {
      devices.value = response.data
    }
  } catch (error) {
    console.error("Error fetching devices:", error)
  } finally {
    isLoading.value = false
  }
}

const generateToken = async () => {
  isGeneratingToken.value = true
  const { post: generateDeviceToken } = useApi({
    url: `/auth/generate-device-token`,
    auth: true,
  })

  try {
    const response = await generateDeviceToken()
    generatedToken.value = response.token
    tokenExpiresAt.value = new Date(response.expires_at).toLocaleString()
    showTokenModal.value = true
    tokenCopied.value = false
  } catch (error) {
    console.error("Error generating token:", error)
    alert("Failed to generate token. Please try again.")
  } finally {
    isGeneratingToken.value = false
  }
}

const copyToken = async () => {
  try {
    await navigator.clipboard.writeText(generatedToken.value)
    tokenCopied.value = true
    setTimeout(() => {
      tokenCopied.value = false
    }, 2000)
  } catch (error) {
    console.error("Error copying token:", error)
  }
}

const openDeviceModal = (device: Device) => {
  selectedDevice.value = device
  showManageModal.value = true
}

const closeManageModal = () => {
  showManageModal.value = false
  selectedDevice.value = null
}

const handleBlockDevice = async (deviceId: number) => {
  const { post: blockDevice } = useApi({
    url: `/devices/block`,
    auth: true,
  })

  try {
    await blockDevice({ device_id: deviceId, block: true })
    closeManageModal()
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
    closeManageModal()
    await fetchDevices()
  } catch (error) {
    console.error("Error unblocking device:", error)
  }
}

const handleDeleteDevice = async (deviceId: number) => {
  const { delete: deleteDevice } = useApi({
    url: `/devices/${deviceId}`,
    auth: true,
  })

  try {
    await deleteDevice()
    closeManageModal()
    await fetchDevices()
  } catch (error) {
    console.error("Error deleting device:", error)
  }
}

const handleDeviceUpdated = () => {
  closeManageModal()
  fetchDevices()
}
</script>

<style scoped></style>
