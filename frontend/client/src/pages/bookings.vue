<template>
  <div>
    <NuxtLayout
      title="Booking management"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <div class="container mx-auto px-2 md:px-4">
        <FilterBar
          :filters-show="filterShow"
          @update:filters="handleFiltersChange"
        />
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <Spinner :is-loading="isLoading" />
          <div
            v-if="bookings.length === 0 && !isLoading"
            :class="`border-white border-opacity-20`"
            class="p-[10px] text-white rounded-[10px] h-full flex items-center justify-center border border-dashed cursor-pointer"
          >
            <div
              class="flex flex-col justify-center text-center items-center m-10"
            >
              <span class="text-xl text-neutral-700"
                >We couldn't find any upcoming bookings</span
              >
            </div>
          </div>
          <BookingCard
            class="border border-white border-opacity-30"
            @manage-booking="openBookingModal"
            @on-favorite-change="getBookings()"
            @onCancelBooking="handleCancelBooking"
            v-for="booking in bookings"
            :key="booking.id"
            :booking="booking"
          />
        </div>
        <div v-if="lastPage > 1" class="flex justify-center mt-4">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage <= 1"
            class=""
          >
            <
          </button>
          <button
            v-for="page in lastPage"
            :key="page"
            @click="goToPage(page)"
            class="px-3 py-1"
          >
            {{ page }}
          </button>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage >= lastPage"
            class=""
          >
            >
          </button>
        </div>
      </div>
      <ManageBookingModal
        v-if="showManageModal && selectedBooking"
        :showPopup="showManageModal"
        :booking="selectedBooking"
        @closePopup="closeManageModal"
        @updated="handleBookingUpdated"
        @on-cancel-booking="handleCancelBooking"
      />
    </NuxtLayout>
  </div>
</template>

<style scoped></style>

<script setup lang="ts">
import { FilterBar } from "~/src/shared/ui/components"
import { computed, onMounted, reactive, ref } from "vue"
import { BookingCard } from "~/src/entities/Booking/ui"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common"
import { filterUnassigned } from "~/src/shared/utils"
import { ManageBookingModal } from "~/src/widgets/Modals"

const showManageModal = ref(false)
const selectedBooking = ref(null)
const filterShow = reactive([
  { key: "search", options: "", value: "" },
  {
    key: "status",
    options: [],
    value: "",
  },
  { key: "date", options: "", value: "" },
  { key: "time", options: "", value: "" },
])

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

const handleFiltersChange = (newFilters) => {
  filterShow.forEach((filter) => {
    filter.value = newFilters[filter.key]
  })
  getBookings(1) // Reset to page 1 with new filters
}

const bookings = ref<Booking[]>([])
const currentPage = ref(1)
const lastPage = ref(1)
const isLoading = ref(true)

onMounted(() => {
  getBookings()
})

const availableStatuses = computed(() => {
  bookings.value.map((booking) => {
    return { id: booking.status.id, name: booking.status.name }
  })
})

const handleCancelBooking = () => {
  closeManageModal()
  getBookings()
}
const getBookings = async (page = 1) => {
  isLoading.value = true
  const { post: fetchBookings } = useApi({
    url: `/booking-management/filter?page=${page}`,
    auth: true,
  })

  const body = filterShow.reduce((acc, filter) => {
    acc[filter.key] = filter.value
    return acc
  }, {})

  const filters = filterUnassigned(body)

  fetchBookings(filters)
    .then((response) => {
      bookings.value = response.data.data

      //Filter by status on frontend
      if (Object.keys(filters).includes("status")) {
        bookings.value = bookings.value.filter(
          (booking) => booking.status.id == filters.status,
        )
      }
      //Update status filter options
      filterShow.find((filter) => filter.key === "status").options = [
        ...new Set(
          bookings.value.reduce((acc, booking) => {
            if (!acc.find((status) => status.id === booking.status.id))
              acc.push({
                id: booking.status.id,
                name:
                  booking.status.name.charAt(0).toUpperCase() +
                  booking.status.name.slice(1),
              })
            return acc
          }, []),
        ),
      ]

      currentPage.value = response.data.current_page
      lastPage.value = response.data.last_page
      isLoading.value = false
    })
    .catch((error) => {
      console.error("Error fetching bookings:", error)
    })
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= lastPage.value) {
    getBookings(page)
  }
}

const openBookingModal = (booking) => {
  selectedBooking.value = booking
  showManageModal.value = true
}

const closeManageModal = () => {
  showManageModal.value = false
  selectedBooking.value = null
}

const handleBookingUpdated = () => {
  closeManageModal()
  getBookings()
}
</script>
