<template>
  <div
    class="bg-black p-4 rounded-md shadow-lg flex flex-col sm:flex-row gap-5 justify-between"
  >
    <div class="flex w-auto justify-between items-center">
      <div class="flex justify-start items-center gap-5">
        <div v-if="booking?.room?.address.company.logo_url" class="h-[35px] w-[35px]">
          <img
            :src="booking?.room?.address.company.logo_url"
            alt="Logo"
            class="h-auto w-full object-cover"
          />
        </div>
        <div class="flex flex-col gap-2">
          <h3 class="text-xl font-bold text-white">
            {{ booking?.room?.address.company.name }}
          </h3>
          <Clipboard
            :text-to-copy="
              phoneNormalizer(booking?.user?.phone || booking?.user.firstname)
            "
          >
            <div
              @mouseenter="
                booking?.user?.phone &&
                  showTooltip(
                    $event,
                    phoneNormalizer(
                      booking?.user?.phone || booking?.user.firstname,
                    ),
                  )
              "
              @mouseleave="hideTooltip"
              class="group flex relative gap-2 items-center justify-start"
            >
              <img
                v-if="booking?.user?.profile_photo"
                :src="booking?.user?.profile_photo"
                class="h-5 w-5 object-contain rounded-full"
              />
              <p class="font-['Montserrat']">
                {{ booking?.user.username || booking?.user.firstname }}
              </p>
            </div>
          </Clipboard>
        </div>
      </div>
    </div>
    <div
      class="flex w-auto flex-col sm:flex-row gap-8 min-w-[210px] justify-center items-start sm:items-center"
    >
      <Clipboard :text-to-copy="booking?.room?.address.street">
        <div class="flex items-center relative gap-2">
          <IconAddress class="opacity-20" />
          <div class="flex flex-col group-hover:opacity-100">
            <span class="text-white opacity-20">Address</span>
            <p class="text-white">{{ booking?.room?.address.street }}</p>
          </div>
        </div>
      </Clipboard>
      <div class="flex items-center relative gap-2 group-hours-block group">
        <IconCalendar class="opacity-20" />
        <div class="flex flex-col group-hover:opacity-100">
          <span class="text-white opacity-20">Date</span>
          <span class="text-white">{{ booking?.date }}</span>
        </div>
      </div>
      <div
        class="flex items-center gap-2 min-w-[210px] relative group-price group"
      >
        <IconClock class="opacity-20" />
        <div class="flex flex-col group-hover:opacity-100">
          <span class="text-white opacity-20">Time</span>
          <span class="text-white"
            >{{ booking?.start_time }} – {{ booking?.end_time }}</span
          >
        </div>
      </div>
    </div>
    <!-- <div class="flex w-auto h-full justify-center items-center">
      <button :class="`border-${getColor(booking?.status.id)} text-${getColor(booking?.status.id)}`" class="w-auto h-11 px-4 hover:opacity-90 bg-transparent border rounded-[10px] text-sm font-medium tracking-wide">
       {{getStatus(booking?.status.id)}}
      </button>
    </div> -->
    <Tooltip> Phone: {{ tooltipData.content }} </Tooltip>
  </div>
</template>

<script setup lang="ts">
import {
  IconCalendar,
  IconCheckmark,
  IconClock,
  IconCopy,
} from "~/src/shared/ui/common"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { getStatus, getColor, phoneNormalizer } from "~/src/shared/utils"
import { inject, ref } from "vue"
import { Tooltip } from "~/src/shared/ui/Tooltip"
import { Clipboard } from "~/src/shared/ui/common/Clipboard"
const { tooltipData, showTooltip, hideTooltip } = inject("tooltipData")
type Booking = {
  id: number
  name: string
  logo: string
  status: number
  isFavorite: boolean
  address: string
  time: string
  date: string
}
const copySuccess = ref(false) // State to track copy success
const props = defineProps<{
  booking: Booking
}>()

const copyToClipboard = (text: string) => {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      copySuccess.value = true // Show notification
      setTimeout(() => (copySuccess.value = false), 2000) // Hide after 2 seconds
    })
    .catch((err) => {
      console.error("Failed to copy:", err)
    })
}
</script>

<style scoped></style>
