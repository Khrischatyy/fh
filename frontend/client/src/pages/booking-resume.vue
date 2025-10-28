<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta, useRuntimeConfig } from "#imports"
import { ref, onMounted, computed } from "vue"
import { useApi } from "~/src/lib/api"
import { navigateTo, useRoute } from "nuxt/app"
import { Spinner, IconLeft } from "~/src/shared/ui/common"
// Meta tags for the page
useHead({
  title: "Funny How – Payment Success",
  meta: [{ name: "description", content: "Processing Payment" }],
})
definePageMeta({
  layout: "error",
})

const route = useRoute()
const isLoading = ref(false)
const errorMessage = ref("")
const sessionId = computed(() => route.query.session_id)
const bookingId = computed(() => route.query.booking_id)

type BookingDataType = {
  addressSlug: string
  room_id: number
  date: string
  start_time: string
  end_time: string
  end_date: string
}

const bookingData = ref<BookingDataType | null>(null)
const bookingError = ref("")
function book(data) {
  isLoading.value = true
  const { post: bookTime } = useApi({
    url: `/reservation`,
    auth: true,
  })

  // Remove booking data from localStorage
  localStorage.removeItem("bookingData")

  bookTime(data)
    .then((response) => {
      isLoading.value = false
      if (response.data?.payment_url) {
        window.location.href = response.data?.payment_url
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      bookingError.value = error.errors.error
      isLoading.value = false
    })
}
const proceedToBooking = () => {
  book(bookingData.value)
}
const backToStudio = () => {
  localStorage.removeItem("bookingData")
  navigateTo(`/@${bookingData.value?.addressSlug}`)
}

onMounted(async () => {
  const storedBookingData = localStorage.getItem("bookingData")
  // if (!storedBookingData) {
  //   navigateTo("/studios")
  //   return
  // }
  bookingData.value = JSON.parse(storedBookingData || "{}")
  // book(bookingData.value)
})
</script>

<template>
  <div>
    <Spinner :is-loading="isLoading" />
    <div v-if="!bookingError && !isLoading" class="error flex flex-col gap-10">
      <div class="text-center">
        <p class="text-xl mb-5">You have an unfinished booking</p>
        <div class="text-sm mb-5 text-left flex flex-col gap-2.5">
          <div class="font-bold">{{ bookingData?.addressSlug }}</div>
          <div class="font-bold">
            From {{ bookingData?.start_time }} {{ bookingData?.date }}
          </div>
          <div class="font-bold">
            To {{ bookingData?.end_time }} {{ bookingData?.end_date }}
          </div>
        </div>
        <p class="text-sm">Do you want to continue?</p>
      </div>
      <div class="flex flex-col justify-center items-center gap-2.5">
        <div class="flex justify-center items-center gap-2.5">
          <button
            @click="proceedToBooking"
            class="max-w-96 px-10 h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-black text-sm font-medium tracking-wide"
          >
            Continue Booking
          </button>
        </div>
        <div class="flex justify-center items-center gap-2.5">
          <button
            @click="backToStudio"
            class="w-full flex justify-center h-11 p-3.5 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            <icon-left />
            Back to Studio Booking
          </button>
        </div>
      </div>
    </div>
    <div v-if="!bookingError && isLoading" class="error flex flex-col gap-10">
      <div class="text-center">
        <p class="text-xl">Processing booking information...</p>
        <p class="text-sm">Please wait a moment</p>
        <p class="text-sm">{{ bookingError }}</p>
      </div>
    </div>
    <div v-if="bookingError" class="flex flex-col gap-5">
      <div class="text-center">
        <h1 class="text-5xl font-bold">Error</h1>
        <p class="text-xl">{{ bookingError }}</p>
      </div>
      <div class="flex justify-center items-center gap-2.5">
        <button
          @click="backToStudio"
          class="max-w-96 px-10 h-11 p-3.5 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
        >
          Go Back To Studio Booking
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #000;
  color: #fff;
  text-align: center;
}
</style>
