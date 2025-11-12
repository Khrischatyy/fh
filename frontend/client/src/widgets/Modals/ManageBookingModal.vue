<script setup lang="ts">
import defaultLogo from "~/src/shared/assets/image/studio.png"
import { Popup } from "~/src/shared/ui/components"
import { getStatus, getColor, getRatingColor } from "~/src/shared/utils"
import { computed, onMounted, ref, watch } from "vue"
import { IconLike } from "~/src/shared/ui/common"
import IconStar from "~/src/shared/ui/common/Icon/IconStar.vue"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common/Spinner"
import FInputClassic from "~/src/shared/ui/common/Input/FInputClassic.vue"
import FSelectClassic from "~/src/shared/ui/common/Input/FSelectClassic.vue"

const props = withDefaults(
  defineProps<{
    showPopup: boolean
    booking: object
  }>(),
  {
    showPopup: false,
  },
)
const isLoading = ref(false)
const isSaving = ref(false)
const availableDevices = ref<any[]>([])

const formData = ref({
  date: '',
  end_date: '',
  start_time: '',
  end_time: '',
  status_id: 1,
  device_id: 0,
})

const emit = defineEmits<{
  (e: "togglePopup"): void
  (e: "closePopup"): void
  (e: "onCancelBooking"): void
  (e: "updated"): void
}>()

const closePopup = () => {
  emit("closePopup")
}

const cancelBooking = async () => {
  isLoading.value = true
  const { post: cancelBooking } = useApi({
    url: "/room/cancel-booking",
    auth: true,
  })

  await cancelBooking({
    booking_id: props.booking?.id,
  }).then((response) => {
    isLoading.value = false
    emit("onCancelBooking", response.data)
    closePopup()
  })
}

const handleSave = async () => {
  isSaving.value = true

  try {
    const { patch: updateBooking } = useApi({
      url: `bookings/${props.booking?.id}`,
      auth: true,
    })

    // Prepare data - convert IDs to integers and device_id 0 to null
    const deviceId = parseInt(formData.value.device_id)
    const statusId = parseInt(formData.value.status_id)

    const dataToSend = {
      date: formData.value.date,
      end_date: formData.value.end_date || null,
      start_time: formData.value.start_time,
      end_time: formData.value.end_time,
      status_id: statusId,
      device_id: deviceId === 0 || !deviceId ? null : deviceId
    }

    const response = await updateBooking(dataToSend)

    if (response.success) {
      emit('updated')
      closePopup()
    }
  } catch (error) {
    console.error('Failed to update booking:', error)
    alert('Failed to update booking. Please try again.')
  } finally {
    isSaving.value = false
  }
}

const loadAvailableDevices = async () => {
  if (!props.booking?.id) return

  try {
    const { fetch: fetchDevices } = useApi({
      url: `bookings/${props.booking.id}/available-devices`,
      auth: true,
    })

    const devicesResponse = await fetchDevices()
    if (devicesResponse.success && devicesResponse.data) {
      availableDevices.value = devicesResponse.data
    }
  } catch (error) {
    console.error('Failed to load devices:', error)
  }
}

// Status options (match database booking_statuses table)
const statusOptions = computed(() => [
  { id: 1, name: 'Pending' },
  { id: 2, name: 'Paid' },
  { id: 3, name: 'Cancelled' },
  { id: 4, name: 'Expired' },
])

// Device options
const deviceOptions = computed(() => {
  const options = [
    { id: 0, name: 'No device' },
  ]

  if (availableDevices.value && availableDevices.value.length > 0) {
    availableDevices.value.forEach((device) => {
      options.push({
        id: device.id,
        name: device.name,
      })
    })
  }

  return options
})

const getFirstPhoto = computed(() => {
  if (!props.booking.room.photos || !props.booking.room.photos.length) {
    return ""
  }
  return props.booking.room.photos[0].path
})

// Watch for booking changes and populate form
watch(() => props.booking, (newBooking) => {
  if (newBooking && props.showPopup) {
    formData.value = {
      date: newBooking.date || '',
      end_date: newBooking.end_date || '',
      start_time: newBooking.start_time || '',
      end_time: newBooking.end_time || '',
      status_id: newBooking.status_id || 1,
      device_id: newBooking.device_id || 0,
    }
    loadAvailableDevices()
  }
}, { immediate: true })
</script>

<template>
  <Popup
    :scroll-to-close="true"
    type="small"
    :title="'Manage Booking'"
    :open="showPopup"
    @close="closePopup"
  >
    <template #header>
      <div class="flex justify-start items-center gap-5">
        <div class="h-[35px] w-[35px]">
          <img
            :src="booking?.room?.address.company.logo_url || defaultLogo"
            alt="Logo"
            class="h-auto w-full object-cover"
          />
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">
            {{ booking?.room?.address.company.name }}
          </h3>
          <p
            :class="`text-${getColor(booking.status.id)}`"
            class="font-['Montserrat']"
          >
            {{ getStatus(booking.status.id) }}
          </p>
        </div>
      </div>
    </template>
    <template #action_header>
      <div
        class="flex items-center gap-3 cursor-pointer justify-end hover:opacity-70"
      >
        <IconLike
          :icon-active="booking?.room?.address.isFavorite"
          :icon-color="booking?.room?.address.isFavorite ? '#FD9302' : 'white'"
        />
      </div>
    </template>
    <template #body>
      <div class="flex flex-col gap-7 justify-between items-center relative">
        <Spinner :is-loading="isLoading" />
        <div v-if="getFirstPhoto" class="w-full relative">
          <img
            :src="getFirstPhoto"
            :alt="booking?.room?.address.company.name"
            class="w-full max-h-48 object-cover rounded-[10px]"
          />
        </div>
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex justify-start gap-2">
            <IconStar class="opacity-20" />
            <div class="relative flex flex-col gap-0.5">
              <span class="text-white opacity-20 text-sm">Rating</span>
              <span :class="`${getRatingColor(booking.room.address.rating)}`">{{
                booking.room.address.rating
              }}</span>
            </div>
          </div>
          <div class="flex justify-start gap-2">
            <IconAddress class="opacity-20" />
            <div class="relative flex flex-col gap-0.5">
              <span class="text-white opacity-20 text-sm">Address</span>
              <span>{{ booking.room.address.street }}</span>
            </div>
          </div>
        </div>
        <div class="w-full grid grid-cols-2 gap-4">
          <!-- Date -->
          <div>
            <label class="text-white opacity-20 text-sm font-normal tracking-wide">Date</label>
            <FInputClassic
              :wide="true"
              type="date"
              v-model="formData.date"
              placeholder="Select date"
            />
          </div>

          <!-- End Date -->
          <div>
            <label class="text-white opacity-20 text-sm font-normal tracking-wide">End Date</label>
            <FInputClassic
              :wide="true"
              type="date"
              v-model="formData.end_date"
              placeholder="Same as start date"
            />
          </div>

          <!-- Start Time -->
          <div>
            <label class="text-white opacity-20 text-sm font-normal tracking-wide">Start Time</label>
            <FInputClassic
              :wide="true"
              type="time"
              v-model="formData.start_time"
              placeholder="Start time"
            />
          </div>

          <!-- End Time -->
          <div>
            <label class="text-white opacity-20 text-sm font-normal tracking-wide">End Time</label>
            <FInputClassic
              :wide="true"
              type="time"
              v-model="formData.end_time"
              placeholder="End time"
            />
          </div>

          <!-- Status -->
          <div>
            <FSelectClassic
              :wide="true"
              label="Status"
              v-model="formData.status_id"
              :options="statusOptions"
              placeholder="Select status"
            />
          </div>

          <!-- Device -->
          <div>
            <FSelectClassic
              :wide="true"
              label="Device"
              v-model="formData.device_id"
              :options="deviceOptions"
              placeholder="No device assigned"
            />
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-between items-center gap-3 w-full">
        <button
          @click="cancelBooking()"
          class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-red border-red border text-sm font-medium tracking-wide"
        >
          Cancel Booking
        </button>
        <button
          @click="handleSave"
          :disabled="isSaving"
          class="w-full h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-black text-sm font-medium tracking-wide disabled:opacity-50"
        >
          {{ isSaving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </template>
  </Popup>
</template>

<style scoped lang="scss"></style>
