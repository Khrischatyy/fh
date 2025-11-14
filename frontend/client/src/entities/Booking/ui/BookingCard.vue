<template>
  <div
    class="bg-black p-4 rounded-md shadow-lg flex flex-col gap-5 justify-between"
  >
    <div class="flex justify-between items-center">
      <div class="flex justify-start items-center gap-5">
        <div class="h-[35px] w-[35px]">
          <img
            :src="booking.room.address.company.logo_url || defaultLogo"
            alt="Logo"
            class="h-auto w-full object-cover"
          />
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">
            {{ booking.room.address.company.name }}
          </h3>
          <p
            :style="`color:${getColorHex(getColor(booking.status.id))}`"
            class="font-['Montserrat']"
          >
            {{ getStatus(booking.status.id) }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-3 cursor-pointer hover:opacity-70">
        <IconLike
          @click.stop="toggleFavorite"
          :icon-active="booking?.room?.address.is_favorite"
          :icon-color="booking?.room?.address.is_favorite ? '#FD9302' : 'white'"
        />
      </div>
    </div>
    <div class="flex gap-3 justify-between items-center relative">
      <div class="w-full relative">
        <Clipboard :text-to-copy="booking.room.address.street">
          <div class="flex items-center relative gap-2">
            <IconAddress class="opacity-20" />
            <p class="text-white">{{ booking.room.address.street }}</p>
          </div>
        </Clipboard>
      </div>
    </div>

    <div class="flex gap-3 justify-between items-center">
      <div class="flex items-center relative gap-2 group-hours-block group">
        <IconCalendar class="opacity-20" />
        <div class="flex flex-col group-hover:opacity-100">
          <span class="text-white opacity-20">Date</span>
          <span class="text-white">{{ formattedDate }}</span>
        </div>
      </div>
      <div class="flex items-center gap-2 relative group-price group">
        <IconClock class="opacity-20" />
        <div class="flex flex-col group-hover:opacity-100">
          <span class="text-white opacity-20">Time</span>
          <span class="text-white">{{ formattedTimeRange }}</span>
        </div>
      </div>
    </div>
    <button
      @click.stop="manageBookingPopup"
      class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
    >
      Manage Booking
    </button>
  </div>
</template>

<script setup lang="ts">
import {
  IconCalendar,
  IconClock,
  IconLike,
} from "~/src/shared/ui/common"
import { getStatus, getColor, getColorHex } from "~/src/shared/utils"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { Clipboard } from "~/src/shared/ui/common/Clipboard"
import defaultLogo from "~/src/shared/assets/image/studio.png"
import { useApi } from "~/src/lib/api"
import { computed } from "vue"

const emit = defineEmits<{
  (e: "onCancelBooking"): void
  (e: "onFavoriteChange", bookingId: number): void
  (e: "manageBooking", booking: any): void
}>()

// Format date from "2025-11-14" to "14 Nov 2025"
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const day = date.getDate()
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const month = months[date.getMonth()]
  const year = date.getFullYear()
  return `${day} ${month} ${year}`
}

// Format time from "18:00:00" to "18:00"
const formatTime = (timeStr: string) => {
  return timeStr.substring(0, 5) // Remove ":00" seconds
}

const formattedDate = computed(() => formatDate(props.booking.date))
const formattedTimeRange = computed(() =>
  `${formatTime(props.booking.start_time)} to ${formatTime(props.booking.end_time)}`
)

const manageBookingPopup = () => {
  emit("manageBooking", props.booking)
}

const toggleFavorite = () => {
  const { post: setFavorite } = useApi({
    url: `/address/toggle-favorite-studio`,
    auth: true,
  })

  setFavorite({ address_id: props.booking?.room?.address.id }).then(() => {
    emit("onFavoriteChange", props.booking.id)
  })
}

type Booking = {
  id: number
  name: string
  logo: string
  status: {
    id: number
  }
  isFavorite: boolean
  address: string
  time: string
  date: string
}

const props = defineProps<{
  booking: Booking
}>()
</script>

<style scoped></style>
