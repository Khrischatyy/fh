<template>
  <div>
    <NuxtLayout
      title="Device Management"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <div class="container mx-auto px-2 md:px-4">
        <!-- Setup Section -->
        <div class="mb-8">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <!-- Step 1: Download App -->
            <div class="bg-neutral-900/60 border border-white/[0.06] rounded-[10px] p-5">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-8 h-8 rounded-full bg-white/[0.08] flex items-center justify-center text-xs font-semibold text-white/60">1</div>
                <span class="text-sm font-medium text-white/90">Download App</span>
              </div>
              <p class="text-xs text-white/40 leading-relaxed mb-4">Install FunnyHow Device Monitor on your Mac.</p>
              <a
                href="/api/downloads/FunnyHow-DeviceMonitor.dmg"
                class="block w-full px-4 py-2.5 bg-white text-black rounded-lg text-sm font-semibold text-center border border-dashed border-white/[0.12]"
                download="FunnyHow-DeviceMonitor.dmg"
              >
                Download .dmg
              </a>
            </div>

            <!-- Step 2: Generate Token -->
            <div class="bg-neutral-900/60 border border-white/[0.06] rounded-[10px] p-5">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-8 h-8 rounded-full bg-white/[0.08] flex items-center justify-center text-xs font-semibold text-white/60">2</div>
                <span class="text-sm font-medium text-white/90">Generate Token</span>
              </div>
              <p class="text-xs text-white/40 leading-relaxed mb-4">Create a secure one-time token for device registration.</p>
              <button
                @click="generateToken"
                :disabled="isGeneratingToken"
                class="w-full px-4 py-2.5 bg-white/[0.06] text-white/50 rounded-lg text-sm font-medium border border-dashed border-white/[0.12] disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {{ isGeneratingToken ? 'Generating...' : 'Generate Token' }}
              </button>
            </div>

            <!-- Step 3: Register -->
            <div class="bg-neutral-900/60 border border-white/[0.06] rounded-[10px] p-5">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-8 h-8 rounded-full bg-white/[0.08] flex items-center justify-center text-xs font-semibold text-white/60">3</div>
                <span class="text-sm font-medium text-white/90">Register</span>
              </div>
              <p class="text-xs text-white/40 leading-relaxed mb-4">Paste the token in the app to link your device.</p>
              <div class="w-full px-4 py-2.5 bg-white/[0.03] border border-dashed border-white/[0.1] rounded-lg text-sm text-white/30 text-center">
                Waiting for device...
              </div>
            </div>
          </div>
        </div>

        <!-- Devices Section -->
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-white/60 uppercase tracking-wider">Your Devices</h3>
          <span class="text-xs text-white/30">{{ devices.length }} device{{ devices.length !== 1 ? 's' : '' }}</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Spinner :is-loading="isLoading" />

          <!-- Empty State -->
          <div
            v-if="devices.length === 0 && !isLoading"
            class="col-span-full bg-neutral-900/40 border border-dashed border-white/[0.08] rounded-[10px] py-16 flex items-center justify-center"
          >
            <div class="flex flex-col justify-center text-center items-center max-w-xs">
              <div class="flex items-center justify-center mb-4">
                <IconMonitor class="w-10 h-10 text-white/20" />
              </div>
              <span class="text-sm font-medium text-white/40">No devices registered yet</span>
              <span class="text-xs text-white/20 mt-1.5 leading-relaxed">
                Follow the steps above to register your first Mac device
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
        class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
        @click.self="showTokenModal = false"
      >
        <div class="bg-[#171717] rounded-[10px] p-5 max-w-md w-full border border-white/[0.08]">
          <!-- Header -->
          <div class="flex justify-between items-start mb-4">
            <div>
              <h2 class="text-base font-semibold text-white mb-1">Token</h2>
              <p class="text-xs text-white/40">Paste this in the FunnyHow app on your Mac</p>
            </div>
            <button
              @click="showTokenModal = false"
              class="w-6 h-6 rounded-md hover:bg-white/[0.08] flex items-center justify-center"
            >
              <svg class="w-3 h-3 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Token Display -->
          <div class="bg-black/40 border border-white/[0.06] rounded-lg px-4 py-3 mb-3 flex items-center justify-between gap-3">
            <code class="text-white/80 font-mono text-xs truncate block">{{ maskedToken }}</code>
            <button
              @click="showFullToken = !showFullToken"
              class="text-[11px] text-white/30 shrink-0"
            >
              {{ showFullToken ? 'Hide' : 'Show' }}
            </button>
          </div>

          <!-- Copy Button -->
          <button
            @click="copyToken"
            class="w-full py-2.5 rounded-lg text-sm font-medium mb-3"
            :class="tokenCopied ? 'bg-transparent text-green-400 border border-green-500/30' : 'bg-transparent text-white/50 border border-dashed border-white/[0.12]'"
          >
            {{ tokenCopied ? 'Copied to clipboard' : 'Copy Token' }}
          </button>

          <!-- Info -->
          <div class="flex items-center justify-between text-[11px] text-white/30">
            <div class="flex items-center gap-3">
              <span>Single-use</span>
              <span class="w-0.5 h-0.5 rounded-full bg-white/20"></span>
              <span>24h expiry</span>
            </div>
            <span>{{ tokenExpiresAt }}</span>
          </div>
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
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
const showFullToken = ref(false)

const maskedToken = computed(() => {
  if (!generatedToken.value) return ''
  if (showFullToken.value) return generatedToken.value
  return generatedToken.value.slice(0, 16) + '••••••••'
})

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
