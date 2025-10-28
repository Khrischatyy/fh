<script setup lang="ts">
import { inject, onMounted, ref } from "vue"
import { IconDown, IconTrash } from "~/src/shared/ui/common"
import { useApi } from "~/src/lib/api"
const emit = defineEmits(["update-studios", "is-ready"])
const prices = ref([])
const props = defineProps<{
      room_id?: number,
    }>()

const pricesList = [
  { hours: 1 },
  { hours: 4 },
  { hours: 8 },
  { hours: 12 },
  { hours: 24 },
]

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

const studio = inject("studioForPopup")

onMounted(async () => {
  if(props.room_id)
    getPrices()
})

function getPrices() {
  isLoading.value = true
  const { fetch } = useApi({
    url: `/room/${props.room_id}/prices`,
    auth: true,
  })
  fetch()
    .then((response) => {
      prices.value = response.data
      isLoading.value = false

    })
    .catch((error) => {
      console.error(error)
    }).finally(() => {
      emit("is-ready")
    })
}

function sendPrice(price) {
  isLoading.value = true
  const { post } = useApi({
    url: `/room/${props.room_id}/prices`,
    auth: true,
  })

  post(price)
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
      emit("update-studios")
    })
    .catch((error) => {
      console.error(error)
    })
}

function deletePrice(price) {
  isLoading.value = true
  const { delete: callDeletePrice } = useApi({
    url: `/room/prices?address_id=${props.room_id}&room_price_id=${price.id}&room_id=${props.room_id}`,
    auth: true,
  })

  if (price.id === undefined) {
    prices.value.splice(index, 1)
    isLoading.value = false
    return
  }

  callDeletePrice()
    .then((response) => {
      prices.value = response.data
      isLoading.value = false
      emit("update-studios")
    })
    .catch((error) => {
      console.error(error)
    })
}

const error = ref(null)
const isLoading = ref(false)
</script>

<template>
  <div class="relative w-full flex-col justify-start items-center gap-2.5 flex">
    <div class="flex-col w-full justify-start items-start gap-1.5 flex">
      <div class="w-full justify-between items-start inline-flex">
        <div class="text-neutral-700 text-sm font-normal tracking-wide">
          Price
        </div>

        <div
          v-if="!isLoading && prices.length == 0"
          class="text-right text-red text-sm font-normal tracking-wide mb-1.5"
        >
          Add at least 1 price package
        </div>
      </div>
      <div
        class="flex-col w-full mb-1 justify-center items-center gap-1.5 flex"
      >
        <div class="justify-center w-full items-center gap-2.5 inline-flex">
          <button
            @click="addPrice()"
            class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-white border-white border text-sm font-medium tracking-wide"
          >
            Add price
          </button>
        </div>
      </div>
      <div
        class="flex-col w-full mb-1 justify-center items-center gap-1.5 flex"
      >
        <div class="justify-center w-full items-center gap-2.5 inline-flex">
          <button
            @click="addSamplePrices()"
            class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-white border-white border text-sm font-medium tracking-wide"
          >
            Replace With Sample Data
          </button>
        </div>
      </div>
    </div>

    <div class="flex-col w-full justify-center items-center gap-1.5 flex">
      <div class="w-full justify-between items-start inline-flex">
        <div class="text-neutral-700 text-sm font-normal tracking-wide">
          You can edit pricing anytime
        </div>
      </div>
      <div v-if="isLoading" class="spinner-container">
        <div class="spinner"></div>
        <!-- Replace with a proper loading indicator -->
      </div>
      <div
        v-for="price in prices"
        :key="price.hours"
        class="relative w-full max-w-full flex items-center gap-1.5 justify-between"
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
          <div class="relative flex w-full items-center pointer-events-none">
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
          @click="deletePrice(price)"
          class="relative cursor-pointer flex items-center"
        >
          <IconTrash />
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
