<template>
  <div class="py-10 px-5">
    <Header />
    <div
      class="ease-in-out min-h-screen mt-10 w-full h-full flex flex-col gap-10 items-center justify-start"
      style="min-height: -webkit-fill-available"
    >
      <div class="flex flex-col gap-5 items-center justify-center">
        <div
          class="text-white w-full flex flex-col justify-center items-center text-5xl font-bold"
        >
          <div
            class="text-white w-full opacity-20 mb-3 text-lg font-['Montserrat'] font-normal tracking-wide"
          >
            Studio name
          </div>
          <div class="flex gap-5 w-full">
            <div v-if="company?.logo_url">
              <img :src="company?.logo_url" class="h-10 w-10 object-contain" />
            </div>
            <div class="font-[BebasNeue] w-full text-left">
              {{ company?.name }}
            </div>
          </div>
        </div>
      </div>
      <div :class="`grid ${gridColumns} gap-10 studio-cards`">
        <StudioCard
          @click="goToStudio(studio)"
          :class="`animate__animated animate__fadeInRight max-w-96 cursor-pointer ${centeredClass}`"
          v-for="studio in filteredStudios"
          :studio="studio"
          :key="studio.id"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { ref, computed, watch, onMounted, type Ref, reactive } from "vue"
import { FSelect } from "~/src/entities/RegistrationForms/ui"
import { StudioCard } from "~/src/entities/Studio"
import {
  getStudios,
  type Studio,
} from "~/src/entities/RegistrationForms/api/getStudios"
import { useAsyncData } from "#app"
import { useRouter, useRoute } from "vue-router"
import {
  getCountries,
  getCities,
  type City,
} from "~/src/entities/RegistrationForms/api"
import { Header } from "~/src/shared/ui/components"
import { FInput } from "~/src/shared/ui/common"
import { navigateTo } from "nuxt/app"
import { useApi } from "~/src/lib/api"

useHead({
  title: "Funny How – Book a Session Time",
  meta: [{ name: "Funny How", content: "Book A Studio Time" }],
})

type SimpleStudio = {
  id: number
  logo: string
  name: string
  address: string
  hours: string
  price: number
  photos: {
    address_id: number
    path: string
    index: number
    url: string
  }
  company?: {
    name: string
    address: string
    logo: string
    slug: string
  }
}

const session = ref()
const searchTerm = ref("")
const selectedCountry = ref<string | null>(null)
const selectedCity = ref<string | null>(null)

const { data: countriesData } = await useAsyncData("countries", getCountries)
const countries = ref(countriesData.value ? countriesData.value : [])

const countryOptions = ref(
  countries.value.map((country) => ({ id: country.id, name: country.name })),
)
const cityOptions: Ref<City[]> = ref([])
const studios: Ref<SimpleStudio[]> = ref([])

const filteredStudios = computed(() => {
  if (!searchTerm.value) {
    return studios.value
  }
  const term = searchTerm.value.toLowerCase()
  return studios.value.filter(
    (studio) =>
      studio.name.toLowerCase().includes(term) ||
      studio.address.toLowerCase().includes(term),
  )
})

const gridColumns = computed(() => {
  if (filteredStudios.value.length === 1) {
    return "md:grid-cols-3 sm:grid-cols-1"
  } else if (filteredStudios.value.length === 2) {
    return "md:grid-cols-2 sm:grid-cols-1"
  } else {
    return "md:grid-cols-3 sm:grid-cols-1"
  }
})

const centeredClass = computed(() => {
  if (filteredStudios.value.length === 1) {
    return "md:col-start-2"
  }
  return ""
})

const goToStudio = (studio) => {
  navigateTo(`/@${studio?.slug}`)
}
const route = useRoute()
const company = ref("")
const getAddresses = async (cityId: string) => {
  const { fetch: getCompany } = useApi({
    url: `/company/${route.params.slug}`,
    auth: true,
  })

  const studiosData = await getCompany()

  company.value = studiosData.data
  studios.value = studiosData.data?.addresses.map((studio) => ({
    id: studio.id,
    logo: company.value.logo_url,
    company: {
      name: company.value.name,
      logo: company.value.logo_url,
      logo_url: company.value.logo_url,
    },
    name: company.value.name,
    street: studio.street,
    photos: studio.photos,
    badges: studio.badges,
    prices: studio.prices,
    slug: studio.slug,
    operating_hours: studio.operating_hours,
    company_slug: company.value.slug,
    price: studio.prices.length > 0 ? studio.prices[0].total_price : 0,
  }))
}

onMounted(() => {
  getAddresses()
})
</script>

<style scoped lang="scss">
.search-input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 100%;
  max-width: 400px;
  margin: 0.5rem 0;
}
.clear-filters-button {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f8f8f8;
  cursor: pointer;
  margin-top: 1rem;
}
</style>
