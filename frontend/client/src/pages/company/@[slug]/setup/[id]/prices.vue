<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta, useRuntimeConfig } from "#imports"
import { useSessionStore } from "~/src/entities/Session"
import { onMounted, ref, type UnwrapRef } from "vue"
import {
  BrandingLogo,
  BrandingLogoSample,
  BrandingLogoSmall,
} from "~/src/shared/ui/branding"
import { navigateTo, useRoute } from "nuxt/app"
import {
  type formValues,
  type inputValues,
  type StudioFormValues,
  useCreateStudioFormStore,
} from "~/src/entities/RegistrationForms"
import {
  IconDown,
  IconElipse,
  IconLeft,
  IconLine,
  IconRight,
  IconTrash,
} from "~/src/shared/ui/common"
import { Loader } from "@googlemaps/js-api-loader"
import axios from "axios"
import { isBadgeTaken } from "~/src/shared/utils/checkBadge"
import { useRouter } from "vue-router"
import FormData from "form-data"
import { useApi } from "~/src/lib/api"
import Spinner from "~/src/shared/ui/common/Spinner/Spinner.vue"
definePageMeta({
  middleware: ["auth"],
})

useHead({
  title: "Dashboard | Prices",
  meta: [{ name: "Funny How", content: "Dashboard" }],
})

const isLoading = ref(false)
const prices = ref([])

const route = useRoute()

const pricesList = [
  { hours: 1 },
  { hours: 4 },
  { hours: 8 },
  { hours: 12 },
  { hours: 24 },
]

function isError(form: string, field: string): boolean {
  let formErrors: Record<string, any> = useCreateStudioFormStore().errors
  return formErrors.hasOwnProperty(field) ? formErrors[field][0] : false
}

function addPrice() {
  // Get all the existing hours from the prices array
  const existingHours = prices.value.map((price) => price.hours)

  // Find the first available hours from pricesList that is not in existingHours
  const nextAvailableHours = pricesList.find(
    (pr) => !existingHours.includes(pr.hours),
  )
  const priceToAdd = {
    total_price: 60 * nextAvailableHours?.hours,
    hours: nextAvailableHours?.hours,
    is_enabled: true,
  }

  // If there's an available hours slot, add a new price with that hours value
  if (nextAvailableHours) {
    sendPrice(priceToAdd)
  } else {
    console.error("No available hours slot to add a new price.")
  }
}

function addSamplePrices() {
  const sampleData = [
    {
      total_price: "60",
      hours: 1,
      is_enabled: false,
    },
    {
      total_price: "240",
      hours: 4,
      is_enabled: false,
    },
    {
      total_price: "360",
      hours: 12,
      is_enabled: false,
    },
  ].filter((price) => !prices.value.some((p) => p.hours === price.hours))
  prices.value.push(...sampleData)
}

onMounted(async () => {
  getPrices()
})

function filterUnassigned(obj) {
  return Object.fromEntries(Object.entries(obj).filter(([_, v]) => v !== ""))
}

function sendPrice(price) {
  isLoading.value = true
  const { post: updatePrice } = useApi({
    url: `/room/${route.query.room_id}/prices`,
    auth: true,
  })

  updatePrice(price)
    .then((response) => {
      response.data.forEach((price, index) => {
        const newOrUpdatePrice = prices.value.find(
          (p) => p.hours === price.hours,
        )
        if (newOrUpdatePrice) {
          newOrUpdatePrice.id = price.id
        } else {
          prices.value.push(price)
        }
      })
      isLoading.value = false
    })
    .catch((error) => {
      console.error(error)
    })
}

function deletePrice(price, index) {
  isLoading.value = true
  const { delete: removePrice } = useApi({
    url: `/room/prices?room_id=${route.query.room_id}&room_price_id=${price.id}`,
    auth: true,
  })

  if (price.id === undefined) {
    prices.value.splice(index, 1)
    isLoading.value = false
    return
  }

  removePrice(price)
    .then((response) => {
      prices.value = response.data
      isLoading.value = false
    })
    .catch((error) => {
      console.error(error)
    })
}
function getPrices() {
  isLoading.value = true
  const { fetch: fetchPrices } = useApi({
    url: `/room/${route.query.room_id}/prices`,
    auth: true,
  })

  fetchPrices().then((response) => {
    if (response.data.length === 0) {
      addSamplePrices()
    }
    prices.value = response.data
    isLoading.value = false
  })
}

function routeBack() {
  navigateTo(`/company/@${route.params.slug}/setup/${route.params.id}/badges?room_id=${route.query.room_id}`)
}


function routeNext() {
  navigateTo(`/my-studios`)
}
</script>

<template>
  <div
    class="grid min-h-screen h-full animate__animated animate__fadeInRight"
    style="min-height: -webkit-fill-available"
  >
    <div
      class="w-full mt-20 h-full flex-col justify-between items-start gap-7 inline-flex px-3"
    >
      <div
        class="relative w-full flex-col justify-start items-center gap-2.5 flex"
      >
        <BrandingLogo class="mb-20" />
        <div class="animate__animated animate__fadeInDown">
          <div
            class="breadcrumbs mb-10 text-white text-sm font-normal tracking-wide flex gap-1.5 justify-center items-center"
          >
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <router-link
              :class="'opacity-20'"
              :to="`/company/@${route.params.slug}/setup/${route.params.id}/hours`"
            >
              Setup Hours
            </router-link>
            <icon-line :class="'opacity-20'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <router-link
              :class="'opacity-20'"
              :to="`/company/@${route.params.slug}/setup/${route.params.id}/badges`"
            >
              Setup Badges
            </router-link>
            <icon-line :class="'opacity-100'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-100'" class="h-4" />
            <router-link
              :class="'opacity-100'"
              :to="`/company/@${route.params.slug}/setup/${route.params.id}/prices`"
            >
              Setup Prices
            </router-link>
          </div>
        </div>

        <div
          class="w-full max-w-96 justify-center items-center inline-flex mb-10 text-center"
        >
          <div class="text-white text-xl font-bold text-center tracking-wide">
            Set Up Prices
          </div>
        </div>

        <div
          class="flex-col justify-start items-start gap-1.5 flex w-full max-w-96"
        >
          <div class="w-full max-w-96 justify-between items-start inline-flex">
            <div class="text-neutral-700 text-sm font-normal tracking-wide">
              Price
            </div>
            <div
              :class="isError('setup', 'studio_name') ? '' : 'hidden'"
              class="text-right text-red-500 text-sm font-normal tracking-wide"
            >
              {{ isError("setup", "studio_name") }}
            </div>
          </div>
          <div
            class="flex-col mb-1 justify-center items-center gap-1.5 flex w-full"
          >
            <div class="justify-center items-center gap-2.5 inline-flex w-full">
              <button
                @click="addPrice()"
                class="w-full max-w-96 h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-white border-white border text-sm font-medium tracking-wide"
              >
                Add price
              </button>
            </div>
          </div>
          <div
            class="flex-col mb-1 justify-center items-center gap-1.5 flex w-full"
          >
            <div class="justify-center items-center gap-2.5 inline-flex w-full">
              <button
                @click="addSamplePrices()"
                class="w-full max-w-96 h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-white border-white border text-sm font-medium tracking-wide"
              >
                Replace With Sample Data
              </button>
            </div>
          </div>
        </div>

        <div class="flex-col justify-center items-center gap-1.5 flex">
          <Spinner :is-loading="isLoading" />
          <div class="w-full max-w-96 justify-between items-start inline-flex">
            <div class="text-neutral-700 text-sm font-normal tracking-wide">
              You can edit pricing anytime
            </div>
            <div
              :class="isError('setup', 'studio_name') ? '' : 'hidden'"
              class="text-right text-red-500 text-sm font-normal tracking-wide"
            >
              {{ isError("setup", "studio_name") }}
            </div>
          </div>
          <div
            v-for="(price, index) in prices"
            :key="price.hours"
            class="animate__animated animate__fadeInDown relative w-full max-w-96 flex items-center gap-1.5 justify-between"
          >
            <label class="checkbox-wrapper flex">
              <div class="w-5 h-5 justify-center items-center flex">
                <input
                  @change="sendPrice(price)"
                  v-model="price.is_enabled"
                  type="checkbox"
                  class="hidden"
                />
                <div
                  class="w-5 h-5 rounded-[5px] border border-white custom-checkbox"
                ></div>
              </div>
            </label>
            <div class="relative w-full flex items-center">
              <div class="flex items-center">
                <select
                  v-model="price.hours"
                  @change="sendPrice(price)"
                  class="w-full opacity-0 absolute top-0 px-3 h-11 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                  name="workday"
                >
                  <option
                    v-for="pr in pricesList"
                    :value="pr.hours"
                    :disabled="prices.some((p) => p.hours === pr.hours)"
                  >
                    {{ pr.hours }}
                  </option>
                </select>
              </div>
              <div class="relative flex items-center pointer-events-none">
                <input
                  disabled
                  :value="price.hours"
                  placeholder="Hours"
                  class="w-full px-3 h-11 outline-none rounded-[10px] focus:border-white border border-neutral-700 border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide"
                  name="workday"
                />
                <span class="absolute right-5 text-neutral-700 cursor-pointer"
                  >hours</span
                >
                <span class="absolute right-0 cursor-pointer">
                  <IconDown />
                </span>
              </div>
            </div>
            <div class="relative w-full flex items-center">
              <input
                @blur="sendPrice(price)"
                v-model="price.total_price"
                type="number"
                placeholder="0"
                class="w-full px-3 h-11 outline-none rounded-[10px] focus:border-white border border-neutral-700 border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide"
                name="price"
              />
              <span class="absolute right-2 text-neutral-700 cursor-pointer"
                >$</span
              >
            </div>
            <div
              @click="deletePrice(price, index)"
              class="relative cursor-pointer flex items-center"
            >
              <IconTrash />
            </div>
          </div>
        </div>

        <div
          class="w-full max-w-96 h-11 p-3.5 mb-5 mt-5 justify-center items-center gap-2.5 inline-flex"
        >
          <button
            @click="routeBack()"
            class="w-full flex justify-start items-center gap-2 h-11 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            <IconLeft />
            <span class="font-light">Back</span>
          </button>
          <button
            @click="routeNext()"
            class="w-full flex justify-end items-center gap-2 h-11 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            <span class="font-light">Next</span>
            <IconRight />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
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
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* For Firefox */
input[type="number"] {
  -moz-appearance: textfield;
}
</style>
