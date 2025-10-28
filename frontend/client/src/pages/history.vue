<template>
  <div>
    <NuxtLayout
      title="History"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <div class="container mx-auto px-2 md:px-4">
        <FilterBar
          :filters-show="filterShow"
          @update:filters="handleFiltersChange"
        />
        <div class="grid grid-cols-1 gap-6">
          <BookingRow
            class="border border-white border-opacity-30"
            v-for="booking in bookings"
            :key="booking.id"
            :booking="booking"
          />
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<style scoped>
.spinner {
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-left-color: #ffffff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

<script setup lang="ts">
import { FilterBar } from "~/src/shared/ui/components"
import { onMounted, reactive, ref } from "vue"
import BookingRow from "~/src/entities/Booking/ui/BookingRow.vue"
import { useApi } from "~/src/lib/api"
import { filterUnassigned } from "~/src/shared/utils"
const showPopup = ref(false)

type BookingRecent = {
  id: number
  name: string
  address: string
  date: string
}

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

const bookings = ref<Booking[]>([])
const currentPage = ref(1)
const lastPage = ref(1)
const isLoading = ref(false)
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

const handleFiltersChange = (newFilters) => {
  filterShow.forEach((filter) => {
    filter.value = newFilters[filter.key]
  })
  getBookings(1) // Reset to page 1 with new filters
}

onMounted(() => {
  getBookings()
})

const getBookings = async (page = 1) => {
  isLoading.value = true
  const { post: fetchBookings } = useApi({
    url: `/history/filter?page=${page}`,
    auth: true,
  })

  const body = filterShow.reduce((acc, filter) => {
    acc[filter.key] = filter.value
    return acc
  }, {})

  const filters = filterUnassigned(body)

  fetchBookings(filterUnassigned(body))
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

const togglePopup = () => {
  showPopup.value = !showPopup.value
}
</script>
