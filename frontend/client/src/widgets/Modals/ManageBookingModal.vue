<script setup lang="ts">
import defaultLogo from "~/src/shared/assets/image/studio.png"
import { Popup } from "~/src/shared/ui/components"
import { getStatus, getColor, getRatingColor } from "~/src/shared/utils"
import { computed, onMounted, onUnmounted, ref } from "vue"
import { IconLike } from "~/src/shared/ui/common"
import IconStar from "~/src/shared/ui/common/Icon/IconStar.vue"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common/Spinner"

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

const emit = defineEmits<{
  (e: "togglePopup"): void
  (e: "closePopup"): void
  (e: "onCancelBooking"): void
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

const getFirstPhoto = computed(() => {
  if (!props.booking.room.photos || !props.booking.room.photos.length) {
    return ""
  }
  return props.booking.room.photos[0].url
})
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
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex justify-start gap-2">
            <div class="relative flex flex-col gap-0.5">
              <span class="text-white opacity-20 text-sm">Date</span>
              <span>{{ booking.date }}</span>
            </div>
          </div>
        </div>
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex justify-start gap-2">
            <div class="relative flex flex-col gap-0.5">
              <span class="text-white opacity-20 text-sm">Start Time</span>
              <span>{{ booking.start_time }}</span>
            </div>
          </div>
          <div class="flex justify-start gap-2">
            <div class="relative flex flex-col gap-0.5">
              <span class="text-white opacity-20 text-sm">End Time</span>
              <span>{{ booking.end_time }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-between items-center gap-2 w-full">
        <button
          @click="cancelBooking()"
          class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-red border-red border text-sm font-medium tracking-wide"
        >
          Cancel Booking
        </button>
      </div>
    </template>
  </Popup>
</template>

<style scoped lang="scss"></style>
