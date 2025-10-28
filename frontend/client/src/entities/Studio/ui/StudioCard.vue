<template>
  <div
      class="bg-black p-4 rounded-md shadow-lg flex flex-col justify-between relative"
  >
    <div class="flex justify-between items-start mb-4">
      <div class="flex justify-start items-center gap-5">
        <img :src="logoSrc" alt="Logo" class="h-[35px] w-[35px]"/>
        <div>
          <h3 class="text-2xl font-bold font-[BebasNeue] text-white">
            {{ studio.company.name }}
          </h3>
          <Clipboard :text-to-copy="studio.street">
            <p class="text-white font-xl font-[BebasNeue]">
              {{ studio.street }}
            </p>
          </Clipboard>
        </div>
      </div>
      <div
          v-if="isDelete"
          @click.stop="openPopup()"
          class="flex items-center gap-3 cursor-pointer hover:opacity-70"
      >
        <IconTrash/>
      </div>
      <div
          v-else
          class="flex flex-col items-center gap-3 cursor-pointer hover:opacity-70"
      >
        <div style="font-size: 1.5rem" class="text-white font-[BebasNeue]">
        </div>
      </div>
    </div>
    <div
        class="flex flex-col justify-center items-center absolute left-0 top-0 w-full h-full"
        v-if="!studio.is_complete"
    >
      <div
          class="absolute bg-black bg-opacity-50 z-20 backdrop-blur-[15px] rounded-[10px] left-0 top-0 w-full h-full"
      ></div>
      <div
          class="flex justify-start z-30 items-center gap-2 px-5 py-2 rounded-[10px] bg-red-500 bg-opacity-0 border-opacity-0 border border-red-500"
      >
        <div class="iconInfo z-30">
          <IconStatus/>
        </div>
        <div class="textInfo z-30">
          <span class="text-white font-['BebasNeue']"
          >Complete setup to publish your studio
          </span>
        </div>
      </div>
      <div
          v-if="!studio?.stripe_account_id"
          class="flex justify-start z-30 items-center gap-2 px-5 py-2 rounded-[10px] bg-red-500 bg-opacity-0 border-opacity-0 border border-red-500"
      >
        <div class="iconInfo z-30">
          <IconDollar/>
        </div>
        <div class="textInfo z-30">
          <span class="text-white font-['BebasNeue']"
          >Add Payout Information
          </span>
        </div>
      </div>
    </div>

    <div class="mt-4 flex gap-3 items-center justify-between relative">
      <PhotoSwipe
          v-if="displayedPhotos.length > 0"
          :photos="displayedPhotos"
          ref="photoSwipe"
          :theme="theme"
          :main-color="mainColor"
      />
      <IconPhotoPlaceholder
          v-for="photo in 3"
          class="h-[80px] sm:h-[80px]"
          v-if="displayedPhotos.length === 0"/>
    </div>

    <div class="mt-5 flex gap-3 w-full justify-center items-center relative">
      <BadgesList
          class="justify-center-important"
          :badges="displayedBadges.slice(0, 4)"
      />
    </div>
    <div class="mt-4 flex gap-3 justify-between items-center">
      <div
          @mouseenter="showTooltip($event, generateTooltipContent('hours'))"
          @click.stop="showTooltip($event, generateTooltipContent('hours'))"
          @mouseleave="hideTooltip"
          class="flex items-center relative group-hours-block group"
      >
        <IconClock class="opacity-20 group-hover:opacity-100"/>
        <div class="flex flex-col group-hover:opacity-100">
          <span
              class="text-white opacity-20 font-['BebasNeue'] group-hover:opacity-100"
          >Working Hours</span
          >
          <span class="text-white font-['BebasNeue']">{{
              todayWorkingHours
            }}</span>
        </div>
      </div>

      <div
          @mouseenter="showTooltip($event, generateTooltipContent('price'))"
          @click.stop="showTooltip($event, generateTooltipContent('price'))"
          @mouseleave="hideTooltip"
          class="flex items-center gap-2 relative group-price group"
      >
        <IconPrice class="opacity-20 group-hover:opacity-100"/>
        <div class="flex flex-col group-hover:opacity-100">
          <span
              class="text-white opacity-20 font-['BebasNeue'] group-hover:opacity-100"
          >Price</span
          >
          <span class="text-white font-['BebasNeue']">{{ primaryPrice }}</span>
        </div>
      </div>
    </div>
    <Tooltip>
      <div class="text-left">
        {{ tooltipData.content }}
      </div>
    </Tooltip>
    <Teleport v-if="showPopup" to="body">
      <Popup
          :title="'Delete Studio'"
          type="small"
          :open="showPopup"
          @close="closePopup"
      >
        <template #header>
          <h1 class="text-white text-[22px]/[26px]">
            You sure you want to delete the studio by {{ studio.street }}?
          </h1>
        </template>
        <template #body>
          <div class="equipment w-full flex flex-col gap-2">
            <FInputClassic
                label="Type in Delete studio to confirm"
                placeholder="Type in Delete studio"
                v-model="deleteConfirmation"
            />
          </div>
        </template>
        <template #footer>
          <div class="flex justify-between items-center gap-2 w-full">
            <button
                @click="closePopup"
                class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-white border-white border text-sm font-medium tracking-wide"
            >
              Cancel
            </button>
            <button
                :disabled="deleteConfirmation.toLowerCase() !== 'delete studio'"
                :class="{
                'opacity-80':
                  deleteConfirmation.toLowerCase() !== 'delete studio',
              }"
                @click="deleteStudio()"
                class="w-full h-11 p-3.5 hover:opacity-80 bg-white rounded-[10px] text-neutral-700 border-white border text-sm font-medium tracking-wide"
            >
              Delete
            </button>
          </div>
        </template>
      </Popup>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import {computed, inject, ref} from "vue"
import IconPrice from "~/src/shared/ui/common/Icon/Filter/IconPrice.vue"
import {
  FInputClassic,
  FSelectClassic,
  IconBooking,
  IconClock,
  IconDollar,
  IconLeft,
  IconLike,
  IconMic,
  IconMonitor, IconPhotoPlaceholder,
  IconRight,
  IconTrash,
} from "~/src/shared/ui/common"

// Import the default images
import defaultLogo from "~/src/shared/assets/image/studio.png"

import defaultPhoto3_1 from "~/src/shared/assets/image/skeleton-studio-card/music-studio.png"
import defaultPhoto3_2 from "~/src/shared/assets/image/skeleton-studio-card/studio.png"
import defaultPhoto3_3 from "~/src/shared/assets/image/skeleton-studio-card/studio-microphone.png"
import {ScrollContainer} from "~/src/shared/ui/common/ScrollContainer"
import {Tooltip} from "~/src/shared/ui/Tooltip"
import {PhotoSwipe} from "~/src/shared/ui/components/PhotoSwipe"
import BadgesList from "~/src/widgets/BadgesChoose/ui/BadgesList.vue"
import {Clipboard} from "~/src/shared/ui/common/Clipboard"
import {Popup} from "~/src/shared/ui/components"
import {useApi} from "~/src/lib/api"
import {IconStatus} from "~/src/shared/ui/common/Icon/Filter"

const props = defineProps({
  studio: {
    type: Object,
    required: true,
  },
  isDelete: {
    type: Boolean,
    default: false,
  },
  theme: {
    type: String,
    default: "default",
  },
  mainColor: {
    type: String,
    default: "black",
  },
})

const emit = defineEmits(["update-studios"])

const showPopup = ref(false)
const openPopup = () => {
  showPopup.value = true
}
const closePopup = () => {
  showPopup.value = false
}

const deleteConfirmation = ref("")
const ICON_MAP = {
  mixing: IconMonitor,
  record: IconMic,
  rent: IconBooking,
}

const {tooltipData, showTooltip, hideTooltip} = inject("tooltipData")

const currentIndex = ref(0)
const badgeIndex = ref(0)

const logoSrc = computed(() => {
  return props.studio.company.logo ? props.studio.company.logo_url : defaultLogo
})

const displayedPhotos = computed(() => {
  let defaultPhotos = [
    {url: defaultPhoto3_1},
    {url: defaultPhoto3_2},
    {url: defaultPhoto3_3},
  ]

  return props.studio.photos
      ? props.studio.photos.sort((a, b) => a.index - b.index)
      : defaultPhotos
})

const displayedBadges = computed(() => {
  return props.studio.badges.slice(badgeIndex.value, 10)
})

// Days of the week in English
const daysOfWeek = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
]

function generateTooltipContent(type) {
  if (type === "hours") {
    let hours = props.studio.operating_hours
    // Sort the hours by day of the week
    hours.sort((a, b) => a.day_of_week - b.day_of_week)

    // Map over the sorted hours to create formatted strings
    return hours
        .map((hour) => {
          const dayName =
              hour.day_of_week === null ? "Everyday" : daysOfWeek[hour.day_of_week]
          const timeString = hour.is_closed
              ? "Closed"
              : `${hour.open_time.substring(0, 5)} - ${hour.close_time.substring(
                  0,
                  5,
              )}`
          return `${dayName}: ${timeString}`
        })
        .join("\n")
  } else if (type === "price") {
    return props.studio.prices
        .map((price) => {
          return `${price.total_price} / ${price.hours} hour`
        })
        .join("\n")
  }
}

const deleteStudio = () => {
  const {post: deleteAddress} = useApi({
    url: `/address/delete-studio`,
    auth: true,
  })

  deleteAddress({address_id: props.studio.id}).then(() => {
    emit("update-studios")
    closePopup()
  })
}

const todayWorkingHours = computed(() => {
  const today = new Date().getDay()
  return "24h"
})

const primaryPrice = computed(() => {
  if (props.studio.prices && props.studio.prices.length > 0) {
    const price = props.studio.prices[0]
    return `$${parseInt(price.total_price)} / ${
        price.hours > 1 ? price.hours + " hours" : "hour"
    }`
  }
  return ""
})
</script>

<style scoped>
.group:hover .group-hover\:opacity-100 {
  opacity: 1 !important;
}

.group-price:hover .group-hover:opacity-100 {
  opacity: 1 !important;
}

.group-hours-block:hover .group-hover:opacity-100 {
  opacity: 1 !important;
}
</style>
