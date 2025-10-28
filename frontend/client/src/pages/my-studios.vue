<template>
  <div>
    <NuxtLayout
      @toggleSideMenu="toggleSideMenu"
      title="Studios"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <Spinner :is-loading="isLoading" />
      <div class="container mx-auto px-2 md:px-4">
        <FilterBar
          :filters-show="filterShow"
          @update:filters="handleFiltersChange"
        />
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <AddStudioButton @click="navigateTo('/create')" />
          <StudioCard
            class="border-dashed border-2 border-opacity-50 hover:border-opacity-100 cursor-pointer"
            @update-studios="fetchStudios"
            :is-delete="true"
            v-for="(studio, index) in myStudios"
            @click="editStudio(index)"
            :key="`${studio.id}_${updateKey}`"
            :studio="studio"
          />
        </div>
      </div>
      <AddStudioModal
        v-if="showPopup"
        :studio-for-popup="studioForPopup"
        :show-popup="showPopup"
        @update-studios="fetchStudios"
        @closePopup="closePopup"
        @togglePopup="togglePopup"
      />
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
import { computed, onMounted, provide, reactive, ref } from "vue"
import { AddStudioButton } from "~/src/features/addStudio"
import { StudioCard } from "~/src/entities/Studio"
import { FilterBar } from "~/src/shared/ui/components"
import { AddStudioModal } from "~/src/widgets/Modals"
import {
  getMyStudiosFilter,
  getCities,
} from "~/src/entities/RegistrationForms/api/getMyStudios"
import { navigateTo } from "nuxt/app"
import { Spinner } from "~/src/shared/ui/common"

const sideMenuRef = ref()
const sideMenuArray = ref([])
const isLoading = ref(true)
const myStudios = ref([])
const showPopup = ref(false)

type Studio = {
  name: string
  address: string
  description: string
  hours: string
  price: number
  logo: string
  badges: string[]
  equipment: string[]
}
const cities = ref([])

const citiesOptions = computed(() => {
  return cities.value.map((city) => ({ id: city.id, name: city.name }))
})

const filterShow = reactive([
  { key: "search", options: "", value: "" },
  { key: "city", options: citiesOptions, value: "" },
  {
    key: "price",
    options: [
      { id: 1, name: "Price 1" },
      { id: 2, name: "Price 2" },
    ],
    value: "",
  },
  {
    key: "rating",
    options: [
      { id: 1, name: "Rating 1" },
      { id: 2, name: "Rating 2" },
    ],
    value: "",
  },
])

const updateKey = ref(0)
const fetchStudios = async () => {
  isLoading.value = true
  myStudios.value = await getMyStudiosFilter(filterShow).catch(() => {
    if(process.client) {
      navigateTo("/create")
      return;
    }
  })

  studioForPopup.value = myStudios.value[indexForPopup.value]
  isLoading.value = false

  updateKey.value += 1
}

const fetchCities = async () => {
  cities.value = await getCities().catch(() => {
    if(process.client) {
      navigateTo("/create")
      return;
    }
  })

}

const handleFiltersChange = (newFilters) => {
  filterShow.forEach((filter) => {
    filter.value = newFilters[filter.key]
  })
  fetchStudios() // Reset to page 1 with new filters
}

const togglePopup = () => {
  showPopup.value = !showPopup.value
}

const studioForPopup = ref<Studio | null>(null)
const indexForPopup = ref(0)

const editStudio = (studioIndex: any) => {
  indexForPopup.value = studioIndex
  studioForPopup.value = myStudios.value[studioIndex]
  showPopup.value = true
}
provide("studioForPopup", studioForPopup)

const closePopup = () => {
  showPopup.value = false
}

const toggleSideMenu = () => {
  if (sideMenuRef.value) {
    sideMenuRef.value.toggleMenu()
  }
}

onMounted(async () => {
  await fetchCities()
  await fetchStudios()
})
</script>
