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
} from "~/src/shared/ui/common"
import { Loader } from "@googlemaps/js-api-loader"
import axios from "axios"
import { type ResponseDto, useApi } from "~/src/lib/api"
import type { Company } from "~/src/entities/RegistrationForms/api"
definePageMeta({
  middleware: ["auth"],
})

useHead({
  title: "Dashboard | Setup",
  meta: [{ name: "Funny How", content: "Dashboard" }],
})

definePageMeta({
  middleware: ["auth"],
})

const isLoading = ref(false)
const workHours = ref({
  mode_id: 1,
  open_time: "10:00",
  close_time: "18:00",
  address_id: "",
  eachDay: [
    {
      day_of_week: 0,
      open_time: "10:00",
      close_time: "18:00",
      is_closed: false,
    },
    {
      day_of_week: 1,
      open_time: "10:00",
      close_time: "18:00",
      is_closed: false,
    },
    {
      day_of_week: 2,
      open_time: "10:00",
      close_time: "18:00",
      is_closed: false,
    },
    {
      day_of_week: 3,
      open_time: "10:00",
      close_time: "18:00",
      is_closed: false,
    },
    {
      day_of_week: 4,
      open_time: "10:00",
      close_time: "18:00",
      is_closed: false,
    },
    {
      day_of_week: 5,
      open_time: "10:00",
      close_time: "18:00",
      is_closed: false,
    },
    {
      day_of_week: 6,
      open_time: "10:00",
      close_time: "18:00",
      is_closed: false,
    },
  ],
})

const modes = ref<Mode[] | undefined>([])

const route = useRoute()

function isError(form: string, field: string): boolean {
  let formErrors: Record<string, any> = useCreateStudioFormStore().errors
  return formErrors.hasOwnProperty(field) ? formErrors[field][0] : false
}

const session = ref()
onMounted(async () => {
  const config = useRuntimeConfig()
  session.value = useSessionStore()
  getModes()
  getOperationHours()
})

function filterUnassigned(obj) {
  return Object.fromEntries(Object.entries(obj).filter(([_, v]) => v !== ""))
}
const getOperationHours = () => {
  const { fetch } = useApi<ResponseDto<Company>>({
    url: `/address/operating-hours?address_id=${route.params.id}`,
    auth: true,
  })

  fetch()
    .then((response) => {
      const operationHours = response?.data
      const mode = operationHours[0]?.mode_id
      switch (mode) {
        case 1:
          workHours.value.mode_id = mode
          break
        case 2:
          workHours.value.mode_id = mode
          workHours.value.open_time = operationHours[0]?.open_time
          workHours.value.close_time = operationHours[0]?.close_time
          break
        case 3:
          workHours.value.mode_id = mode
          workHours.value.eachDay = operationHours.map((day) => {
            return {
              day_of_week: day.day_of_week,
              open_time: day.open_time,
              close_time: day.close_time,
              is_closed: day.is_closed,
            }
          })
          break
      }
    })
    .catch((error) => {
      console.error("error", error)
    })
}

function setHours() {
  const { post } = useApi<ResponseDto<Company>>({
    url: `/address/operating-hours`,
    auth: true,
  })
  let data
  switch (workHours.value.mode_id) {
    case 1:
      data = {
        mode_id: workHours.value.mode_id,
        address_id: route.params.id,
      }
      break
    case 2:
      data = {
        mode_id: workHours.value.mode_id,
        address_id: route.params.id,
        open_time: workHours.value.open_time,
        close_time: workHours.value.close_time,
      }
      break
    case 3:
      data = {
        mode_id: workHours.value.mode_id,
        address_id: route.params.id,
        hours: workHours.value.eachDay,
      }
      break
  }
  post(data)
    .then((response) => {
      routeNext()
    })
    .catch((error) => {
      console.error("error", error)
    })
}

type Mode = {
  id: number
  mode: string
  description: string
}

function getModes() {
  const api = useApi<ResponseDto<Mode[]>>({
    url: "/operation-modes",
    auth: true,
  })

  api
    .fetch()
    .then((response) => {
      modes.value = response?.data
    })
    .catch((error) => {
      console.error("error", error)
    })
}

function getFormValues(): StudioFormValues {
  return useCreateStudioFormStore().inputValues
}

function routeBack() {
  navigateTo(`/create`)
}

function routeNext() {
  navigateTo(`/company/@${route.params.slug}/setup/${route.params.id}/badges?room_id=${route.query.room_id}`)
}

function signOut() {
  session.value.logout()
}
const getDayMean = (day: number) => {
  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ]
  return days[day]
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
        <div class="animate__animated animate__fadeInRight">
          <div
            class="breadcrumbs mb-10 text-white text-sm font-normal tracking-wide flex gap-1.5 justify-center items-center"
          >
            <icon-elipse :class="'opacity-100'" class="h-4" />
            <button :class="'opacity-100'">Setup Hours</button>
            <icon-line :class="'opacity-100'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <router-link
              :class="'opacity-20'"
              :to="`/company/@${route.params.slug}/setup/${route.params.id}/badges`"
            >
              Setup Badges
            </router-link>
            <icon-line :class="'opacity-20'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <router-link
              :class="'opacity-20'"
              :to="`/company/@${route.params.slug}/setup/${route.params.id}/prices`"
            >
              Setup Prices
            </router-link>
          </div>
        </div>

        <div
          class="max-w-96 w-full justify-center items-center inline-flex mb-10 text-center"
        >
          <div class="text-white text-xl font-bold text-center tracking-wide">
            Set Up Hours
          </div>
        </div>

        <div class="flex-col justify-start items-start gap-1.5 flex">
          <div class="max-w-96 w-full justify-between items-start inline-flex">
            <div class="text-white text-sm font-normal tracking-wide">
              Working hours
            </div>
            <div
              :class="isError('setup', 'studio_name') ? '' : 'hidden'"
              class="text-right text-red-500 text-sm font-normal tracking-wide"
            >
              {{ isError("setup", "studio_name") }}
            </div>
          </div>
        </div>

        <div class="flex-col justify-center items-center gap-1.5 flex w-full">
          <div
            class="max-w-96 w-full justify-center items-center gap-2.5 inline-flex"
          >
            <div class="max-w-96 w-full relative">
              <div class="flex items-center">
                <select
                  :class="workHours.mode_id == 3 ? 'opacity-0 absolute' : ''"
                  v-model="workHours.mode_id"
                  class="w-full top-0 px-3 h-11 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                  name="workday"
                >
                  <option
                    v-for="mode in modes"
                    class="text-white"
                    :value="mode.id"
                  >
                    {{ mode.label }}
                  </option>
                </select>
                <span
                  v-if="workHours.mode_id != 3"
                  class="absolute right-0 cursor-pointer"
                >
                  <IconDown />
                </span>
              </div>
              <div
                v-if="workHours.mode_id == 3"
                class="relative flex items-center pointer-events-none"
              >
                <input
                  disabled
                  placeholder="Weekday Hours"
                  class="w-full px-3 h-11 outline-none rounded-[10px] focus:border-white border border-white border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide"
                  name="workday"
                />
                <span class="absolute right-0 cursor-pointer">
                  <IconDown />
                </span>
              </div>
            </div>

            <div
              v-if="workHours.mode_id == 2"
              class="gap-2.5 inline-flex justify-center items-center"
            >
              <input
                v-model="workHours.open_time"
                step="3600"
                class="w-full h-11 px-3 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                type="time"
                placeholder="From"
              />
              <input
                v-model="workHours.close_time"
                step="3600"
                class="w-full h-11 px-3 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                type="time"
                placeholder="To"
              />
            </div>
          </div>
          <div
            v-for="(hour, index) in 7"
            v-if="workHours.mode_id == 3"
            class="max-w-96 w-full justify-center items-center gap-2.5 inline-flex"
          >
            <div class="max-w-96 w-full max-w-96">
              <input
                disabled
                :placeholder="getDayMean(index)"
                class="w-full px-3 h-11 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                name="workday"
              />
            </div>
            <div class="gap-2.5 inline-flex justify-center items-center">
              <input
                v-model="workHours.eachDay[index].open_time"
                class="w-full h-11 px-3 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                type="time"
                placeholder="From (Weekend)"
              />
              <input
                v-model="workHours.eachDay[index].close_time"
                class="w-full h-11 px-3 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                type="time"
                placeholder="To (Weekend)"
              />
            </div>
          </div>
        </div>

        <div
          class="max-w-96 w-full h-11 p-3.5 mb-5 mt-5 justify-center items-center gap-2.5 inline-flex"
        >
          <button
            disabled
            class="disabled:opacity-20 flex justify-start items-center gap-2 h-11 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            <IconLeft />
            <span class="font-light">Back</span>
          </button>
          <button
            @click="setHours()"
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
</style>
