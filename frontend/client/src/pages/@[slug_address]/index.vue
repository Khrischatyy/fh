<template>
  <div
      ref="mainContainer"
      class="grid min-h-screen pb-[400px] overflow-hidden h-full bg-black"
      style="min-height: -webkit-fill-available"
  >
    <Spinner :is-loading="!address"/>
    <div
        v-if="address && address.is_complete"
        ref="photoContainer"
        style="width: -webkit-fill-available"
        class="photo-container animate__animated animate__fadeInDown w-full max-h-[250px] max-w-full backdrop-blur p-0 py-5 md:p-10"
    >
      <div
          ref="pswpElement"
          class="pswp"
          tabindex="-1"
          role="dialog"
          aria-hidden="true"
      ></div>
      <div v-if="address?.photos?.length === 0" class="w-full flex justify-center items-center">
        <div class="text-white text-2xl font-[BebasNeue] text-center">
          Studio owner didn't add photos
        </div>
      </div>
      <ScrollContainer
          v-if="address?.photos?.length > 0"
          :justify-content="address?.photos?.length >= 7 ? 'start' : 'center'"
          justofy-content-mobile="start"
          class="rounded-[10px] h-full"
          theme="default"
          main-color="#171717"
      >
        <div
            v-for="(photo, index) in address?.photos.sort(
            (a, b) => a.index - b.index,
          )"
            class="max-h-30 max-w-[250px] bg-white shadow rounded-[10px] scrollElement"
        >
          <img
              :src="photo.path"
              @click.stop="() => openGallery(displayedPhotos, index)"
              alt="cover photo"
              class="w-full h-full object-cover rounded-[10px]"
          />
        </div>
      </ScrollContainer>
    </div>
    <div
        class="info-container w-full animate__animated animate__fadeInRight h-full flex-col justify-between items-start gap-7 inline-flex"
    >
      <div
          v-if="address && address.is_complete"
          class="relative w-full flex-col justify-start items-center gap-2.5 flex"
      >
        <div class="p-5 md:p-0 max-w-96 sm:max-w-3xl sm:w-full flex flex-col items-center justify-center">
          <div
              class="max-w-96 w-full flex items-center justify-center gap-2 mt-5 mb-5"
          >
            <div
                class="text-white w-full flex flex-col justify-center items-center text-5xl font-bold"
            >
              <div
                  @click="navigateTo('/studios')"
                  class="text-white cursor-pointer w-full opacity-20 hover:opacity-100 mb-3 flex gap-3 justify-end items-center text-xs font-['Montserrat'] font-normal tracking-wide"
              >
                <IconBackDraw class="w-3"/>
                All Studios
              </div>
              <div
                  class="text-white w-full opacity-20 mb-3 text-sm font-['Montserrat'] font-normal tracking-wide"
              >
                Studio name
              </div>
              <div class="flex gap-5 w-full">
                <div v-if="address?.company?.logo_url">
                  <img
                      :src="address?.company?.logo_url"
                      class="h-10 w-10 object-contain"
                  />
                </div>
                <div class="font-[BebasNeue] w-full text-left">
                  {{ address?.company.name }}
                </div>
              </div>
            </div>
          </div>
          <div
              class="max-w-96 w-full justify-between gap-1.5 items-center flex-col mb-10 text-center"
          >
            <div
                class="text-white mb-10 text-5xl font-light text-left tracking-wide"
            >
              <div
                  class="text-white opacity-20 mb-3 text-sm font-['Montserrat'] font-normal tracking-wide"
              >
                Address
              </div>
              <Clipboard :text-to-copy="address?.street">
                <div class="flex gap-5 w-full">
                  <div>
                    <IconAddress class="h-10 w-10 object-contain"/>
                  </div>
                  <div class="font-[BebasNeue] text-4xl w-full text-left">
                    {{ address?.street }}<br/>
                  </div>
                </div>
              </Clipboard>
            </div>
            <div
                class="max-w-[300px] w-full justify-start gap-2.5 items-center inline-flex mb-10 text-center"
                style="width: -webkit-fill-available"
            >
              <BadgesList
                  justify-content="center"
                  theme="default"
                  size="lg"
                  style="width: -webkit-fill-available"
                  :badges="address?.badges"
              />
            </div>
            <div
                class="max-w-96 w-full justify-center gap-3.5 items-center flex mb-10 text-center"
            >
              <div
                  v-for="price in uniquePrices"
                  class="price-tag flex flex-col gap-1 text-white justify-center items-center"
              >
                <div class="mb-2">
                  <IconPricetag/>
                </div>
                <div
                    class="font-[BebasNeue] text-3xl flex justify-center items-center"
                >
                  {{ price.hours }} HOUR{{ price.hours > 1 ? "S" : "" }}
                </div>
                <div class="font-['Montserrat']">${{ price.total_price }}</div>
              </div>
            </div>
            <div
                class="max-w-96 w-full justify-center gap-3.5 items-center flex mb-10 text-center"
            >
              <div
                  class="price-tag flex gap-2 font-[BebasNeue] text-4xl text-white justify-center items-center"
              >
                Rating:
                <span :class="getRatingColor(address?.rating)">{{
                    address?.rating
                  }}</span>
              </div>
            </div>
            <div
                v-if="address?.equipments.length > 0"
                @click="openEquipmentsPopup"
                class="relative flex items-center m-auto cursor-pointer max-w-[211px] input border border-white border-double"
            >
              <button
                  class="w-full px-3 h-11 font-['BebasNeue'] flex justify-center items-center outline-none bg-transparent text-white text-2xl text-center font-medium tracking-wide"
              >
                Equipments
              </button>
            </div>
            <div
                v-if="!isOwner"
                @click="openChatPopup"
                class="relative flex items-center m-auto cursor-pointer max-w-[211px] input border border-white border-double"
            >
              <button
                  class="w-full px-3 h-11 font-['BebasNeue'] flex justify-center items-center outline-none bg-transparent text-white text-2xl text-center font-medium tracking-wide"
              >
                Chat
              </button>
            </div>
          </div>
          <div
              class="max-w-[514px] w-full justify-between gap-1.5 items-center flex-col mb-10 text-center"
          >
            <div class="w-full max-w-[514px] h-[313px] relative">
              <a
                  :href="`https://www.google.com/maps?q=${address?.latitude},${address?.longitude}`"
                  target="_blank"
                  class="nav group absolute z-10 w-full h-full group bg-black cursor-pointer bg-opacity-70 hover:bg-opacity-90 transition duration-300 flex justify-center items-center"
              >
                <div
                    class="navigate-button font-[BebasNeue] group-hover:scale-115 transition duration-300 text-2xl text-white flex gap-3 justify-center items-center"
                >
                  <IconNav class="w-[20px] h-[20px]"/>
                  Direction
                </div>
              </a>
              <GoogleMap
                  class=""
                  :logo="address?.company.logo_url"
                  :lat="address?.latitude"
                  :lng="address?.longitude"
              />
            </div>
          </div>
          <div v-if="address?.rooms.length > 0"
               class="flex flex-col items-center w-full text-center">
            <div class="flex gap-2 font-[BebasNeue] text-4xl text-white justify-center mt-5 items-center underline underline-offset-4 mb-5">
              ROOM:
            </div>
            <div class="flex flex-row gap-4 justify-center w-full max-w-[1200px] overflow-x-auto">
              <div v-for="room in address?.rooms.filter(r => r.prices.length > 0)"
                   @click="chooseRoom(room.id)"
                   class="flex-shrink-0 w-[150px] md:w-[250px] lg:w-[300px] h-[150px] md:h-[250px] lg:h-[300px]">
                <RoomCard
                    class="w-full h-full"
                    :class="room.id === rentingForm.room_id ? 'border border-white' : 'border border-transparent'"
                    :room="room"
                />
              </div>
            </div>
          </div>
          <div
              v-if="address"
              class="max-w-[212px] m-auto w-full justify-between gap-1.5 items-center flex-col text-center mb-10"
          >
            <div
                class="underline underline-offset-4 flex gap-2 font-[BebasNeue] text-4xl text-white justify-center mt-10 md:mt-10 mb-2 items-center"
            >
              Engineer:
            </div>
            <div class="relative w-full flex flex-col items-center">
              <div class="flex items-center flex-col z-[55] w-full">
                <FSelect
                    class="w-full"
                    modelKey="id"
                    v-model="rentingForm.engineer_id"
                    placeholder="Choose Engineer"
                    :options="teammatesOptions"/>
              </div>

            </div>

          </div>
          <div
              v-if="address"
              class="max-w-[212px] m-auto w-full justify-between gap-1.5 items-center flex-col mb-10 text-center"
          >
            <div
                class="underline underline-offset-4 flex gap-2 font-[BebasNeue] text-4xl text-white justify-center mb-2 items-center"
            >
              Day:
            </div>
            <div v-if="rentingForm.room_id" class="relative w-full flex items-center">
              <div class="flex items-center flex-col w-full">
                <SelectPicker
                    :timezone="address?.timezone"
                    class="w-full z-50"
                    @dateSelected="dateChanged($event, 'date')"
                />
              </div>
            </div>

            <div
                v-if="rentingForm.date == 'another-day'"
                class="relative w-full flex items-center mt-3"
            >
              <div class="flex items-center">
                <input
                    v-model="rentingForm.anotherDate"
                    name="date"
                    type="date"
                    ref="dateInput"
                    class="w-full px-3 h-11 outline-none rounded-[10px] opacity-0 absolute focus:border-white border border-neutral-700 border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide"
                />
              </div>
              <div
                  @click="openDatePicker('date')"
                  class="relative w-full flex items-center"
              >
                <input
                    :value="rentingForm.anotherDate"
                    placeholder="Choose Another Day"
                    class="pointer-events-none w-full px-3 h-11 outline-none rounded-[10px] focus:border-white border border-neutral-700 border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide"
                    name="workday"
                />
                <span class="absolute right-5 text-neutral-700 cursor-pointer"
                >Day</span
                >
                <span class="absolute right-0 cursor-pointer">
                  <IconDown/>
                </span>
              </div>
            </div>

            <div
                v-if="rentingForm.date && hoursAvailableStart.length == 0"
                class="relative w-full flex flex-col max-w-[212px] items-center"
            >
              <div
                  class="flex gap-2 font-[BebasNeue] text-l text-white justify-center mt-5 mb-2 items-center"
              >
                No available slots at this time
              </div>
            </div>
            <div
                v-if="rentingForm.date && hoursAvailableStart.length > 0"
                class="relative w-full max-w-[212px] flex flex-col items-center mt-10"
            >
              <div
                  class="flex gap-2 font-[BebasNeue] text-4xl text-white justify-center mt-5 mb-2 items-center"
              >
                Start From
              </div>
              <TimeSelect
                  :key="rentingForm.date"
                  class="z-40"
                  :available-hours="hoursAvailableStart"
                  label="Start From"
                  placeholder="Choose Start Time"
                  renting-form="rentingForm"
                  @timeChanged="timeChanged($event, 'start_time')"
              />
            </div>

            <div
                v-if="
                rentingForm['start_time'] &&
                rentingForm.date &&
                hoursAvailableEnd.length > 0
              "
                class="relative w-full flex flex-col max-w-[212px] mb-10 items-center"
            >
              <div
                  class="flex gap-2 font-[BebasNeue] text-4xl text-white justify-center mt-5 mb-2 items-center"
              >
                To
              </div>
              <TimeSelect
                  class="z-30"
                  :key="rentingForm.start_time.time && rentingForm.date"
                  :available-hours="hoursAvailableEnd"
                  label="To"
                  placeholder="Choose End Time"
                  renting-form="rentingForm"
                  @timeChanged="timeChanged($event, 'end_time')"
              />
            </div>
          </div>
          <div
              :key="rentingForm.start_time.time"
              v-if="calculatedPrice"
              class="flex-col mb-14 relative justify-center items-center gap-1.5 flex animate__animated animate__fadeInDown"
          >
            <div
                class="relative w-full max-w-48 mx-auto mb-5 flex justify-between items-center animate__animated animate__fadeInDown"
            >
              <div class="text-white text-4xl font-[BebasNeue]">Price:</div>
              <div
                  @click.stop="
                  showTooltip($event, calculatedPrice?.explanation || '')
                "
                  @mouseenter="
                  showTooltip($event, calculatedPrice?.explanation || '')
                "
                  @mouseleave="hideTooltip"
                  @touchstart="
                  showTooltip($event, calculatedPrice?.explanation || '')
                "
                  @touchend="hideTooltip"
                  class="text-white text-4xl flex items-center justify-between gap-2 relative font-[BebasNeue]"
              >
                <span
                    class="text-white text-4xl flex gap-2 relative font-[BebasNeue]"
                >$<DisplayNumber :value="calculatedPrice?.total_price"
                /></span>
                <IconStatus/>
              </div>
            </div>
            <div v-if="isLoading" class="spinner-container">
              <div class="spinner"></div>
            </div>
            <Spinner :is-loading="isLoading"/>
            <div class="flex justify-center items-center flex-col gap-2">
              <div
                  class="text-white opacity-70 text-sm font-normal font-['Montserrat'] tracking-wide"
              >
                We accept
              </div>
              <div class="justify-center items-center flex gap-5 mb-10">
                <IconApplePay/>
                <IconGooglePay/>
                <IconVisa/>
                <IconMastercard/>
              </div>
            </div>
            <div v-if="bookingError" class="errors mb-5">
              <div class="text-red-500 text-sm">{{ bookingError }}</div>
            </div>

            <div
                @click="book()"
                class="relative w-full flex items-center m-auto cursor-pointer max-w-[211px] input border border-white border-double"
            >
              <button
                  class="w-full px-3 h-11 font-['BebasNeue'] flex justify-center items-center outline-none bg-transparent text-white text-2xl text-center font-medium tracking-wide"
              >
                Rent
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="isOwner && customers.length">
        <div class="mb-4 text-white">Выберите клиента для чата:</div>
        <div class="flex flex-col gap-2 mb-6">
          <button v-for="id in customers" :key="id" @click="openChatWithCustomer(id)" class="bg-gray-800 text-white rounded px-4 py-2 hover:bg-blue-600">
            Чат с клиентом #{{ id }}
          </button>
        </div>
      </div>
    </div>
    <EquipmentsModal
        v-if="showPopup"
        :showPopup="showPopup"
        @closePopup="closePopup"
    />
    <LoginModal
        v-if="showLoginPopup"
        :show-popup="showLoginPopup"
        @close-popup="closeLoginPopup"
    />
    <ChatModal
      v-if="showChatPopup && ((isOwner && selectedCustomerId) || (!isOwner && address?.company?.user_id))"
      :showPopup="showChatPopup"
      :studioId="address?.id"
      :recipientId="isOwner ? selectedCustomerId : address?.company?.user_id"
      @closePopup="showChatPopup = false"
    />
  </div>
</template>
<script setup lang="ts">
import {useHead} from "@unhead/vue"
import {definePageMeta, storeToRefs, useRuntimeConfig} from "#imports"
import {useSessionStore} from "~/src/entities/Session"
import {EquipmentsModal, LoginModal} from "~/src/widgets/Modals"
import {
  computed,
  inject,
  onBeforeMount,
  onMounted,
  onUnmounted,
  provide,
  type Ref,
  ref,
  watch,
  watchEffect,
} from "vue"
import {navigateTo, useRoute} from "nuxt/app"
import {
  type StudioFormValues,
  useCreateStudioFormStore,
} from "~/src/entities/RegistrationForms"
import {
  IconDown,
  IconMastercard,
  IconApplePay,
  IconVisa,
  IconGooglePay,
  IconMic,
  IconBackDraw,
  IconNav,
  IconPricetag,
  Spinner,
} from "~/src/shared/ui/common"
import GoogleMap from "~/src/widgets/GoogleMap.vue"
import {SelectPicker} from "~/src/features/DatePicker"
import {TimeSelect} from "~/src/widgets"
import {type ResponseBrand, useAddress} from "~/src/entities/Studio/api"
import BadgesList from "~/src/widgets/BadgesChoose/ui/BadgesList.vue"
import {ScrollContainer} from "~/src/shared/ui/common/ScrollContainer"
import {usePhotoSwipe} from "~/src/shared/ui/components/PhotoSwipe"
import type {SlideData} from "photoswipe"
import {useApi} from "~/src/lib/api"
import paymentSystems from "~/src/shared/assets/image/payment_systems.png"
import {useSeoMeta} from "unhead"
import {DisplayNumber} from "~/src/shared/ui/components"
import {getRatingColor} from "~/src/shared/utils"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import {Clipboard} from "~/src/shared/ui/common/Clipboard"
import FSelect from "~/src/shared/ui/common/Input/FSelect.vue"
import {IconStatus} from "~/src/shared/ui/common/Icon/Filter"
import {RoomCard} from "~/src/entities/Studio";
import ChatModal from '~/src/components/ChatModal.vue'

const route = useRoute()
const addressSlug = ref(route.params.slug_address)
const bookingError = ref("")
const {address} = useAddress(addressSlug.value)
const {tooltipData, showTooltip, hideTooltip} = inject("tooltipData")
provide("address", address)

const teammatesOptions = computed(() => {
  // Check if the address and engineers are defined
  const engineers = address?.value?.engineers ?? [];

  // Map engineers to the desired format
  const options = engineers.map((teammate) => ({
    id: teammate.id,
    name: `${teammate.username} / $${teammate?.engineer_rate?.rate_per_hour}`,
    label: `${teammate.username} / $${teammate?.engineer_rate?.rate_per_hour}`,
  }));

  // Add the first option "No Engineer"
  options.unshift({
    id: null,
    name: "No Engineer",
    label: "No Engineer",
  });

  return options;
});


const roomsOptions = computed(() => address.value?.rooms.map((room) => ({
  id: room.id,
  name: room.name,
  label: room.name,
})))
const pageTitle: Ref<string> = computed(() => {
  return address.value
      ? `${address.value.company.name} | Recording Studio`
      : "Loading..."
})

const pageDescription: Ref<string> = computed(() => {
  return address.value && address.value.prices.length > 0
      ? `Book a session at ${address.value.company.name} from $${address.value.prices[0]?.price_per_hour}/hour. Only at Funny-How.com`
      : "Book a session only at Funny-How.com"
})
const studioFirstPhoto: Ref<string> = computed(() => {
  return address.value && address?.value?.photos.length > 0
      ? address?.value?.photos[0].url
      : "/meta/open-graph-image.png"
})
const isLoading = ref(false)

const session = useSessionStore()

const {isAuthorized} = storeToRefs(session)

const dateInput = ref<HTMLInputElement | null>(null)
const end_time = ref<HTMLInputElement | null>(null)
const start_time = ref<HTMLInputElement | null>(null)

type StudioFormValues = {
  address_id: string
  date: string
  start_time: string
  end_time: string
}
const rentingForm = ref({
  room_id: "",
  engineer_id: "",
  address_id: "",
  date: "",
  anotherDate: "",
  start_time: {
    time: "",
    date: "",
  },
  end_time: {
    time: "",
    date: "",
  },
})
const today = new Date()
const tomorrow = new Date()
tomorrow.setDate(today.getDate() + 1)
const hoursAvailableStart = ref([])
const hoursAvailableEnd = ref([])
const rentingList = [
  {name: "today", date: ""},
  {name: "tomorrow", date: ""},
  {name: "another-day", date: "another-day"},
]
rentingList[0].date = today.toISOString().split("T")[0]
rentingList[1].date = tomorrow.toISOString().split("T")[0]

const setSeoMeta = () => {
  useSeoMeta({
    title: () => `${address.value?.company.name} - Funny How`,
    description: () =>
        `Book a session at ${address.value.company.name} from $${address.value.prices[0]?.price_per_hour}/hour. Only at Funny-How.com`,
    ogTitle: `${address.value?.company.name} - Funny How`,
    ogDescription: () =>
        `Book a session at ${address.value.company.name} from $${address.value.prices[0]?.price_per_hour}/hour. Only at Funny-How.com`,
    ogImage: () => `${address?.value?.photos[0].url}`,
    ogUrl: route.fullPath,
    twitterTitle: () => `${address.value?.company.name} - Funny How`,
    twitterDescription: () =>
        `Book a session at ${address.value.company.name} from $${address.value.prices[0]?.price_per_hour}/hour. Only at Funny-How.com`,
    twitterImage: `${address?.value?.photos[0].url}`,
    twitterCard: "summary",
  })

  useHead({
    title: pageTitle,
    meta: [{name: "description", content: pageDescription.value}],
    htmlAttrs: {
      lang: "en",
    },
    link: [
      {
        rel: "icon",
        type: "image/png",
        href: "/favicon.png",
      },
    ],
  })
}

useSeoMeta({
  title: () => `${address.value?.company.name} - Funny How`,
  description: () =>
      `Book a session at ${address.value?.company.name} from $${address.value?.prices[0]?.price_per_hour}/hour. Only at Funny-How.com`,
  ogTitle: `${address.value?.company.name} - Funny How`,
  ogDescription: () =>
      `Book a session at ${address.value?.company.name} from $${address.value?.prices[0]?.price_per_hour}/hour. Only at Funny-How.com`,
  ogImage: () => {
    const photos = address?.value?.photos
    return photos && photos.length > 0
        ? photos[0].url
        : "/meta/open-graph-image.png"
  },
  ogUrl: route.fullPath,
  twitterTitle: () => `${address.value?.company.name} - Funny How`,
  twitterDescription: () =>
      `Book a session at ${address.value?.company.name} from $${address.value?.prices[0]?.price_per_hour}/hour. Only at Funny-How.com`,
  twitterImage: () => {
    const photos = address?.value?.photos
    return photos && photos.length > 0
        ? photos[0].url
        : "/meta/open-graph-image.png"
  },
  twitterCard: "summary",
})

useHead({
  title: pageTitle,
  meta: [{name: "description", content: pageDescription}],
  htmlAttrs: {
    lang: "en",
  },
  link: [
    {
      rel: "icon",
      type: "image/png",
      href: "/favicon.png",
    },
  ],
})

const photoContainer = ref<HTMLElement | null>(null)

const handleScroll = () => {
  if (!photoContainer.value) return
  const maxHeight = 250 // Max height of the photo container
  const minHeight = 150 // Min height of the photo container
  const scrollThreshold = 0 // Scroll position at which the resizing effect should start

  const scrollPosition = window.scrollY
  if (scrollPosition < scrollThreshold) {
    photoContainer.value.style.height = `${maxHeight}px`
  } else {
    const newHeight = Math.max(
        minHeight,
        maxHeight - (scrollPosition - scrollThreshold),
    )
    photoContainer.value.style.height = `${newHeight}px`
  }
}

onBeforeMount(() => {
  if (address.value && !address.value.is_complete) {
    navigateTo("/studios")
  }
})

onMounted(async () => {
  window.addEventListener("scroll", handleScroll)
  window.addEventListener("message", handlePaymentStatus)

  photoContainer.value?.addEventListener("animationend", () => {
    mainContainer.value.style.overflow = "inherit"
  })
  if (address?.value?.rooms?.length > 0) {
    rentingForm.value.room_id = address?.value?.rooms[0].id
  }
  if (isOwner.value) fetchCustomersForOwner()
})

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll)
  window.removeEventListener("message", handlePaymentStatus)
})

function handlePaymentStatus(event: MessageEvent) {
  if (event.origin !== window.location.origin) return // Ensure the message is from the same origin
  if (event.data && event.data.status === "closed") {
    // Handle the status update here
  }
}

async function getStartSlots() {
  const {fetch: fetchStartSlots} = useApi({
    url: `/address/reservation/start-time?room_id=${rentingForm.value.room_id}&date=${rentingForm.value.date}`,
  })

  fetchStartSlots().then((response) => {
    hoursAvailableStart.value = response.data
  })
}

async function getEndSlots(start_time: string) {
  const {fetch: getEndSlots} = useApi({
    url: `/address/reservation/end-time?room_id=${rentingForm.value.room_id}&date=${rentingForm.value.date}&start_time=${start_time}`,
  })

  getEndSlots().then((response) => {
    hoursAvailableEnd.value = response.data
  })
}

const calculatedPrice = ref(0)

const chooseRoom = (roomId: string) => {
  rentingForm.value.room_id = roomId
  getStartSlots()
}

const uniquePrices = computed(() => {
  return address.value?.prices.reduce((acc, price) => {
    if (!acc.find((p) => p.hours === price.hours)) {
      acc.push(price)
    }
    return acc
  }, [])
})
const calculatePrice = () => {
  const {post: getPrice} = useApi({
    url: `/address/calculate-price`,
    auth: true,
  })

  getPrice({
    room_id: rentingForm.value.room_id,
    engineer_id: rentingForm.value.engineer_id,
    start_time:
        rentingForm.value.start_time.date +
        "T" +
        rentingForm.value.start_time.time,
    end_time:
        rentingForm.value.end_time.date + "T" + rentingForm.value.end_time.time,
  }).then((response) => {
    calculatedPrice.value = response.data
  })
}

watch(
    () => rentingForm.value.start_time,
    (newVal) => {
      if (newVal && rentingForm.value.end_time) {
        calculatedPrice.value = 0
        rentingForm.value.end_time = {
          time: "",
          date: "",
        }
      }
    },
)
watch(
    () => rentingForm.value.end_time,
    (newVal) => {
      if (newVal && rentingForm.value.end_time.time) {
        calculatePrice()
      }
    },
)
watch(
    () => rentingForm.value.date,
    (newVal) => {
      if (newVal) {
        calculatedPrice.value = 0
        rentingForm.value.end_time = {
          time: "",
          date: "",
        }
      }
    },
)
watch(
    () => rentingForm.value.room_id,
    (newVal) => {
      if (newVal) {
        rentingForm.value.date = ""
        rentingForm.value.start_time = {
          time: "",
          date: "",
        }
        rentingForm.value.end_time = {
          time: "",
          date: "",
        }
        calculatedPrice.value = 0

      }
    },
)

watch(
    () => rentingForm.value.engineer_id,
    (newVal) => {
      if (rentingForm.value.start_time.date && rentingForm.value.end_time.date) {
        calculatePrice()
      }
    },
)
export type reservationResponse = {
  address_id: number
  start_time: string
  end_time: string
  total_cost: number
  date: string
  updated_at: string
  created_at: string
  id: number
}

const responseQuote = ref({})
watchEffect(() => {
  if (
      rentingForm.value.start_time ||
      rentingForm.value.end_time ||
      rentingForm.value.date || rentingForm.value.room_id
  ) {
    bookingError.value = ""
  }

})

function book() {
  isLoading.value = true
  const {post: bookTime} = useApi({
    url: `/room/reservation`,
    auth: true,
  })

  const bookingData = {
    addressSlug: addressSlug.value,
    room_id: rentingForm.value.room_id,
    engineer_id: rentingForm.value.engineer_id,
    date: rentingForm.value.date,
    start_time: rentingForm.value.start_time.time,
    end_time: rentingForm.value.end_time.time,
    end_date: rentingForm.value.end_time.date,
  }

  // Store booking data in localStorage
  localStorage.setItem("bookingData", JSON.stringify(bookingData))
  if (!isAuthorized.value) {
    openLoginPopup()
    isLoading.value = false
    return
  }
  bookTime(bookingData)
      .then((response) => {
        responseQuote.value = response.data
        isLoading.value = false
        //Delete bookingData from local storage if success and redirect to payment
        localStorage.removeItem("bookingData")
        if (response.data?.payment_url) {
          window.location.href = response.data?.payment_url
        }
      })
      .catch((error) => {
        localStorage.removeItem("bookingData")
        bookingError.value = error.errors.error
        isLoading.value = false
      })
}

function pay(url: string) {
  const paymentWindow = window.open(
      url,
      "_blank",
      "width=800,height=600,toolbar=0,location=0,menubar=0",
  )

  const checkWindowClosed = setInterval(() => {
    if (paymentWindow && paymentWindow.closed) {
      clearInterval(checkWindowClosed)
      window.postMessage({status: "closed"}, window.location.origin)
    }
  }, 500)
}

function openDatePicker(input) {
  if (input == "date") dateInput.value[0].showPicker()
  else if (input == "start_time") {
    start_time.value[0].showPicker()
  } else if (input == "end_time") {
    end_time.value[0].showPicker()
  }
}

type DateReponse = {
  date: string
}

function dateChanged(newDate: DateReponse, input: keyof StudioFormValues) {
  rentingForm.value[input] = newDate?.date
  getStartSlots()
}

function timeChanged(newDate: string, input: keyof StudioFormValues) {
  if (input == "start_time") {
    rentingForm.value[input] = newDate
    getEndSlots(newDate.time)
    return
  }

  rentingForm.value[input] = newDate
}

const {pswpElement, openGallery} = usePhotoSwipe()
const displayedPhotos: SlideData[] = computed(() =>
    address?.value.photos.map((photo) => ({
      src: photo.path,
      w: photo.file?.width || 1200, // Default width if not specified
      h: photo.file?.height || 900, // Default height if not specified
    })),
)
const mainContainer = ref<HTMLElement | null>(null)
const showPopup = ref(false)
const showLoginPopup = ref(false)
const openEquipmentsPopup = () => {
  showPopup.value = true
}
const openLoginPopup = () => {
  showLoginPopup.value = true
}
const closePopup = () => {
  showPopup.value = false
}
const closeLoginPopup = () => {
  showLoginPopup.value = false
}

const showChatPopup = ref(false)
const isAuth = ref(false)
const studioId = ref(null)
const studioOwnerId = ref(null)

const openChatPopup = () => {
  console.log('[chat][debug] Opening chat popup')
  console.log('[chat][debug] isOwner:', isOwner.value)
  console.log('[chat][debug] address?.company?.user_id:', address.value?.company?.user_id)
  console.log('[chat][debug] selectedCustomerId:', selectedCustomerId.value)
  showChatPopup.value = true
}

const closeChatPopup = () => {
  showChatPopup.value = false
}

watchEffect(() => {
  console.log('address:', address.value);
  console.log('user_id:', address.value?.company?.user_id);
  console.log('showChatPopup:', showChatPopup.value);
});

const isOwner = computed(() => session.user?.id === address.value?.company?.user_id)
const selectedCustomerId = ref(null)
const customers = ref([])

async function fetchCustomersForOwner() {
  // Получаем всю историю сообщений для адреса (можно оптимизировать на бэкенде)
  const { fetch } = useApi({
    url: `/messages/history?address_id=${address.value.id}&user_id=${session.user?.id}`,
    auth: true
  })
  const response = await fetch()
  if (response?.data) {
    // Собираем уникальные customer_id (sender_id, не равные owner)
    const ids = new Set()
    response.data.forEach(msg => {
      if (msg.sender_id !== session.user?.id) ids.add(msg.sender_id)
      if (msg.recipient_id !== session.user?.id) ids.add(msg.recipient_id)
    })
    customers.value = Array.from(ids)
  }
}

function openChatWithCustomer(customerId) {
  selectedCustomerId.value = customerId
  showChatPopup.value = true
}
</script>

<style scoped lang="scss">
:deep(body),
:deep(html) {
  background-color: rgb(15 14 14);
}

.shadow-text {
  text-shadow: 2px 3px 1px rgba(0, 0, 0, 0.8), 12px 14px 1px rgba(0, 0, 0, 0.8);
}

.checkbox-wrapper {
  display: flex;
  gap: 5px;
  cursor: pointer;

  .custom-checkbox {
    display: inline-block;
    vertical-align: middle;
    position: relative;

    &:after {
      content: "";
      position: absolute;
      display: none;
    }
  }

  input[type="checkbox"] {
    &:checked ~ .custom-checkbox {
      padding: 3px;
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;

      &:after {
        position: relative;
        top: 0;
        left: 0;
        display: block;
        width: 100%;
        height: 100%;
        border: solid white;
        background: #f3f5fd;
        border-radius: 2px;
      }
    }
  }
}

select {
  -webkit-appearance: none;
  -moz-appearance: none;
  text-indent: 1px;
  text-overflow: "";
  cursor: pointer;
}

.photo-container {
  top: 0;
  transition: height 0.1s ease-in-out;
  z-index: 1000;
}
</style>
