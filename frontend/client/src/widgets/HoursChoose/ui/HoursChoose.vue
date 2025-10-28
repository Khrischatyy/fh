<script setup lang="ts">
import { useSessionStore } from "~/src/entities/Session"
import { inject, onMounted, ref, watch } from "vue"
import { navigateTo, useRoute } from "nuxt/app"
import {
  type StudioFormValues,
  useCreateStudioFormStore,
} from "~/src/entities/RegistrationForms"
import { IconDown, Spinner } from "~/src/shared/ui/common"

import { useAsyncData } from "#app"
import { getModes } from "~/src/widgets/HoursChoose/api"
import { type ResponseDto, useApi } from "~/src/lib/api"
import type { Company } from "~/src/entities/RegistrationForms/api"

const emit = defineEmits(["update-studios"])
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

const modes = ref([])
const studio = inject("studioForPopup")
const route = useRoute()
const isLoading = ref(false)
const updateKey = ref(0)
function isError(form: string, field: string): boolean {
  let formErrors: Record<string, any> = useCreateStudioFormStore().errors
  return formErrors.hasOwnProperty(field) ? formErrors[field][0] : false
}

const session = ref()
onMounted(async () => {
  session.value = useSessionStore()
  await getOperationHours()
})

function filterUnassigned(obj) {
  return Object.fromEntries(Object.entries(obj).filter(([_, v]) => v !== ""))
}

function setHours() {
  isLoading.value = true
  const { post } = useApi<ResponseDto<Company>>({
    url: `/address/operating-hours`,
    auth: true,
  })
  let data
  switch (workHours.value.mode_id) {
    case 1:
      data = {
        mode_id: workHours.value.mode_id,
        address_id: studio?.value.id,
      }
      break
    case 2:
      data = {
        mode_id: workHours.value.mode_id,
        address_id: studio?.value.id,
        open_time: workHours.value.open_time,
        close_time: workHours.value.close_time,
      }
      break
    case 3:
      data = {
        mode_id: workHours.value.mode_id,
        address_id: studio?.value.id,
        hours: workHours.value.eachDay,
      }
      break
  }
  post(data)
    .then((response) => {
      isLoading.value = false
      updateKey.value++
      emit("update-studios")
    })
    .catch((error) => {
      console.error("error", error)
      updateKey.value++
      isLoading.value = false
    })
}

const { data, error } = useAsyncData("operationModes", getModes)

if (data.value) {
  modes.value = data.value.data
}
watch(
  data,
  (newData) => {
    if (newData) {
      modes.value = newData.data || []
    }
  },
  { immediate: true },
)

const getOperationHours = async () => {
  const { fetch } = useApi<ResponseDto<Company>>({
    url: `/address/operating-hours?address_id=${studio?.value.id}`,
    auth: true,
  })
  isLoading.value = true
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
      isLoading.value = false
    })
    .catch((error) => {
      console.error("error", error)
      isLoading.value = false
    })
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
    class="relative w-full flex-col justify-start items-center gap-1.5 flex"
  >
    <div class="flex-col w-full justify-start items-start gap-1.5 flex">
      <div class="w-full justify-between items-start inline-flex">
        <div class="text-white opacity-20 text-sm font-normal tracking-wide">
          Working hours
        </div>
        <div
          v-if="
            !isLoading && studio?.operating_hours.length == 0 && updateKey == 0
          "
          class="text-right text-red text-sm font-normal tracking-wide mb-1.5"
        >
          Update your working hours
        </div>
      </div>
    </div>

    <div
      class="flex-col w-full justify-center items-center relative gap-1.5 flex"
    >
      <div class="w-full justify-center items-center gap-2.5 inline-flex">
        <Spinner :is-loading="isLoading" />
        <div class="w-full max-w-full relative">
          <div class="flex items-center">
            <select
              :class="workHours.mode_id == 3 ? 'opacity-0 absolute' : ''"
              v-model="workHours.mode_id"
              class="w-full top-0 px-3 h-11 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
              name="workday"
            >
                <option v-for="mode in modes" class="text-white" :value="mode.id">
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
              placeholder="Custom Hours For Each Day"
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
            class="w-full h-11 px-3 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
            type="time"
            placeholder="From"
          />
          <input
            v-model="workHours.close_time"
            class="w-full h-11 px-3 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
            type="time"
            placeholder="To"
          />
        </div>
      </div>
      <div
        v-for="(hour, index) in 7"
        v-if="workHours.mode_id == 3"
        class="w-full justify-center items-center gap-2.5 inline-flex"
      >
        <div class="w-full ">
          <input
            disabled
            :placeholder="getDayMean(workHours.eachDay[index].day_of_week)"
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
      <button
        @click="setHours"
        class="w-full h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-700 border-white border text-sm font-medium tracking-wide mt-2"
      >
        Update
      </button>
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
