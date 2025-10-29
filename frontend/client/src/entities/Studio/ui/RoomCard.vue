<template>
  <div
    class="bg-[#010907] h-full max-h-[150px] sm:max-h-[234px] rounded-md shadow-lg flex flex-col justify-between relative border border-dashed border-white  duration-300 hover:scale-105 transform-gpu origin-center"
  >
    <div class="flex justify-between items-start mb-4">
      <button
          v-if="displayedPhotos.length > 1"
          @click.stop="prevPhoto"
          class="cursor-pointer w-auto opacity-60 hover:opacity-100 rounded-tr-[10px] rounded-tb-[10px] backdrop-blur-[1px] h-full bg-gradient-to-r to-transparent rounded-lg absolute flex items-center justify-start left-0 border-none p-0 z-10"
      >
        <IconLeft iconType="thin" />
      </button>
      <button
          v-if="displayedPhotos.length > 1"
          @click.stop="nextPhoto"
          class="cursor-pointer w-auto opacity-60 hover:opacity-100 rounded-tl-[10px] rounded-bl-[10px] backdrop-blur-[1px] h-full bg-gradient-to-l to-transparent rounded-lg absolute flex items-center justify-end right-0 border-none p-0 z-10"
      >
        <IconRight iconType="thin" />
      </button>
      <div class="flex justify-start w-full rounded-md z-50 items-center gap-5">
        <div
            :class="{ 'bg-gradient-to-t from-transparent to-black': displayedPhotos.length > 1 }"
            class="w-full rounded-md p-4">
          <h3 class="text-l text-white">
            {{ room.name }}
          </h3>
        </div>
      </div>
      <div
        v-if="isDelete"
        @click.stop="openPopup()"
        class="flex items-center gap-3 cursor-pointer hover:opacity-70"
      >
        <IconTrash />
      </div>
    </div>

    <div
        :style="`background: url(${displayedPhotos[currentIndex]?.path}) rgb(33 33 33) no-repeat center center / cover;`"
        class="flex flex-col gap-1 h-full w-full justify-center items-center absolute top-0 left-0 rounded-md cursor-pointer">
      <div v-if="displayedPhotos.length === 0" class="flex flex-col items-center justify-center">
        <IconPhotoPlaceholder class="h-[50px] sm:h-[100px]" />
        <p class="text-white opacity-5 text-xs font-medium mt-1">Photo is not added</p>
      </div>
    </div>
    <div class="mt-0 sm:mt-4 flex gap-3 justify-between rounded-md items-center">
      <div
        @mouseenter="generateTooltipContent('price') && showTooltip($event, generateTooltipContent('price'))"
        @click.stop="showTooltip($event, generateTooltipContent('price'))"
        @mouseleave="hideTooltip"
        :class="{ 'bg-gradient-to-b from-transparent to-black': displayedPhotos.length > 1 }"
        class="flex p-4 items-center rounded-md z-50 w-full gap-2 relative group-price group"
      >
        <IconPrice class="opacity-20 group-hover:opacity-100" />
        <div class="flex flex-col gap-2 group-hover:opacity-100">
          <span
            class="text-white opacity-20 text-sm group-hover:opacity-100 w-full text-left"
            >Price</span
          >
          <span class="text-white text-xs w-full text-left">{{ primaryPrice }}</span>
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
            You sure you want to delete the studio by {{ room.name }}?
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
import {computed, inject, ref, watch, watchEffect} from "vue"
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
import { ScrollContainer } from "~/src/shared/ui/common/ScrollContainer"
import { Tooltip } from "~/src/shared/ui/Tooltip"
import { PhotoSwipe } from "~/src/shared/ui/components/PhotoSwipe"
import BadgesList from "~/src/widgets/BadgesChoose/ui/BadgesList.vue"
import { Clipboard } from "~/src/shared/ui/common/Clipboard"
import { Popup } from "~/src/shared/ui/components"
import { useApi } from "~/src/lib/api"
import { IconStatus } from "~/src/shared/ui/common/Icon/Filter"

const props = defineProps({
  room: {
    type: Object,
    required: true,
  },
  isDelete: {
    type: Boolean,
    default: false,
  },
})

const photosUpdated = ref(0)

watch(() => props.room.photos, () => {
  photosUpdated.value++
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

const { tooltipData, showTooltip, hideTooltip } = inject("tooltipData")

const currentIndex = ref(0)
const badgeIndex = ref(0)

const displayedPhotos = computed(() => {
  let defaultPhotos = [
    { path: defaultPhoto3_1 },
    { path: defaultPhoto3_2 },
    { path: defaultPhoto3_3 },
  ]

  return props.room.photos
    ? props.room.photos.sort((a, b) => a.index - b.index)
    : defaultPhotos
})

const prevPhoto = () => {
  if (currentIndex.value === 0) {
    currentIndex.value = displayedPhotos.value.length - 1
  } else {
    currentIndex.value--
  }
}

const nextPhoto = () => {
  if (currentIndex.value === displayedPhotos.value.length - 1) {
    currentIndex.value = 0
  } else {
    currentIndex.value++
  }
}

function generateTooltipContent(type) {
  if (type === "price") {
    return props.room.prices
      .map((price) => {
        return `${price.total_price} / ${price.hours} hour`
      })
      .join("\n")
  }
}
const deleteStudio = () => {
  const { post: deleteAddress } = useApi({
    url: `/address/delete-studio`,
    auth: true,
  })

  deleteAddress({ address_id: props.room.id }).then(() => {
    emit("update-studios")
    closePopup()
  })
}

const todayWorkingHours = computed(() => {
  const today = new Date().getDay()
  return "24h"
})

const primaryPrice = computed(() => {
  if (props.room.prices && props.room.prices.length > 0) {
    const price = props.room.prices[0]
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
