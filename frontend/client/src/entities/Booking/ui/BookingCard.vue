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
          @click="toggleFavorite"
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
          <span class="text-white">{{ booking.date }}</span>
        </div>
      </div>
      <div class="flex items-center gap-2 relative group-price group">
        <IconClock class="opacity-20" />
        <div class="flex flex-col group-hover:opacity-100">
          <span class="text-white opacity-20">Time</span>
          <span class="text-white"
            >{{ booking.start_time }} – {{ booking.end_time }}</span
          >
        </div>
      </div>
    </div>
    <button
      v-if="booking.status.id == BookingStatus.Paid"
      @click="manageBookingPopup"
      class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
    >
      Manage Booking
    </button>
    <button
      v-if="
        booking.status.id == BookingStatus.Pending &&
        booking?.user_id == user?.id &&
        booking?.temporary_payment_link
      "
      @click="goToPay(booking?.temporary_payment_link)"
      class="w-full h-11 hover:opacity-90 border border-red-500 rounded-[10px] text-red-500 bg-red-500 bg-opacity-5 text-sm font-medium tracking-wide"
    >
      Pay
    </button>
    <ManageBookingModal
      v-if="showPopup"
      @on-cancel-booking="handleCancelBooking"
      :showPopup="showPopup"
      :booking="booking"
      @closePopup="closePopup"
    />
  </div>
</template>

<script setup lang="ts">
import {
  IconCalendar,
  IconClock,
  IconLeft,
  IconLike,
  IconRight,
} from "~/src/shared/ui/common"
import { BookingStatus } from "~/src/shared/utils"
import { ManageBookingModal } from "~/src/widgets/Modals"
import { ref } from "vue"
import { getStatus, getColor, getColorHex } from "~/src/shared/utils"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { Clipboard } from "~/src/shared/ui/common/Clipboard"
import defaultLogo from "~/src/shared/assets/image/studio.png"
import { useApi } from "~/src/lib/api"
import { useSessionStore } from "~/src/entities/Session"
import { storeToRefs } from "pinia"
const showPopup = ref(false)
const session = useSessionStore()
const { user } = storeToRefs(session)
// const user = session.getUser()
const emit = defineEmits<{
  (e: "onCancelBooking"): void
  (e: "onFavoriteChange", bookingId: number): void
}>()

const closePopup = () => {
  showPopup.value = false
}
const manageBookingPopup = () => {
  showPopup.value = true
}
const handleCancelBooking = (bookings) => {
  emit("onCancelBooking", bookings)
}
const goToPay = (url) => {
  window.location.href = url
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
