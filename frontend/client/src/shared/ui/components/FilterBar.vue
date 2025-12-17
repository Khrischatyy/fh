<template>
  <div
    class="flex flex-col lg:grid lg:grid-cols-3 lg:justify-between items-center gap-2 md:gap-[20px] mb-6 space-y-4 lg:space-y-0 w-full"
  >
    <!-- Search and IconButton on the first line -->
    <div class="flex items-center w-full">
      <FInputClassic
        :wide="true"
        placeholder="Search"
        v-model="filters.search"
        @click="makeActive('search')"
        v-click-outside="resetActive"
        class="w-full"
      >
        <template #icon>
          <IconSearch
            :active="activeFilter == 'search'"
            class="h-5 w-5 text-gray-400"
          />
        </template>
      </FInputClassic>
      <IconButton
        @click="openFiltersToogle"
        :isActive="isFiltersOpen"
        class="ml-2 lg:hidden open-filters"
      />
    </div>

    <template v-if="isFiltersOpen">
      <!-- Status and Price on the second line -->
      <div class="flex items-center w-full flex-col lg:flex-row gap-6">
        <div class="flex w-full h-full gap-[20px]">
          <FSelectClassic
            v-if="getFilterShow('city')"
            @click="makeActive('city')"
            v-click-outside="resetActive"
            placeholder="City"
            :options="getFilterShow('city')?.options"
            v-model="filters.city"
            class="w-full h-[43px]"
          >
            <template #icon>
              <IconStatus
                :active="activeFilter == 'city'"
                lass="h-5 w-5 text-gray-400"
              />
            </template>
          </FSelectClassic>
          <FSelectClassic
            v-if="getFilterShow('status')"
            @click="makeActive('status')"
            v-click-outside="resetActive"
            placeholder="Status"
            :options="getFilterShow('status')?.options"
            v-model="filters.status"
            class="w-full h-[43px]"
          >
            <template #icon>
              <IconStatus
                :active="activeFilter == 'status'"
                class="h-5 w-5 text-gray-400"
              />
            </template>
          </FSelectClassic>
          <FSelectClassic
            v-if="getFilterShow('badges')"
            placeholder="Badges"
            @click="makeActive('badges')"
            v-click-outside="resetActive"
            :options="getFilterShow('badges')?.options"
            v-model="filters.badges"
            class="w-full h-[43px]"
          >
            <template #icon>
              <IconStatus
                :active="activeFilter == 'badges'"
                class="h-5 w-5 text-gray-400"
              />
            </template>
          </FSelectClassic>

          <FInputClassic
            v-if="getFilterShow('date')"
            type="date"
            @click="makeActive('date')"
            v-click-outside="resetActive"
            placeholder="Date"
            v-model="filters.date"
            size="sm"
            class="w-full h-[43px]"
          >
            <template #icon>
              <IconCalendar
                :active="activeFilter == 'date'"
                class="h-5 w-5 text-gray-400"
              />
            </template>
          </FInputClassic>

          <FInputClassic
            v-if="getFilterShow('price')"
            @click="makeActive('price')"
            v-click-outside="resetActive"
            placeholder="Price up to"
            size="sm"
            v-model="filters.price"
            class="w-full h-[43px]"
          >
            <template #icon>
              <IconPrice
                :active="activeFilter == 'price'"
                class="h-5 w-5 text-gray-400"
              />
            </template>
          </FInputClassic>
        </div>
      </div>

      <!-- Rating, Filter, Clear Filter on the third line -->
      <div class="flex w-full justify-end items-center gap-6">
        <FInputClassic
          v-if="getFilterShow('time')"
          type="time"
          @click="makeActive('time')"
          v-click-outside="resetActive"
          placeholder="Time"
          v-model="filters.time"
          size="sm"
          class="max-w-[117px] md:max-w-full w-full h-[43px]"
        >
          <template #icon>
            <IconClock
              :active="activeFilter == 'time'"
              class="h-5 w-5 text-gray-400"
            />
          </template>
        </FInputClassic>
        <FInputClassic
          v-if="getFilterShow('rating')"
          placeholder="Rating"
          @click="makeActive('rating')"
          v-click-outside="resetActive"
          size="sm"
          v-model="filters.rating"
          class="max-w-[117px] md:max-w-full w-full h-[43px]"
        >
          <template #icon>
            <IconRating
              :active="activeFilter == 'rating'"
              class="h-5 w-5 text-gray-400"
            />
          </template>
        </FInputClassic>
        <div
          class="bg-white text-black py-2 px-[10px] rounded-[10px] w-[71px] md:w-full h-[43px] flex items-center justify-center text-[14px] leading-[17px] tracking-[0.04em]"
        >
          Filter
        </div>
        <div
          @click="clearFilters"
          class="border border-red-500 py-2 px-1 rounded-[10px] w-full h-[43px] flex items-center justify-center text-red-500 text-[14px] leading-[17px] tracking-[0.04em]"
        >
          Clear filter
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import IconPrice from "~/src/shared/ui/common/Icon/Filter/IconPrice.vue"
import IconRating from "~/src/shared/ui/common/Icon/Filter/IconRating.vue"
import IconSearch from "~/src/shared/ui/common/Icon/Filter/IconSearch.vue"
import IconStatus from "~/src/shared/ui/common/Icon/Filter/IconStatus.vue"
import IconButton from "~/src/shared/ui/common/Icon/Filter/IconButton.vue"
import {
  FInput,
  FInputClassic,
  FSelectClassic,
  IconCalendar,
  IconClock,
} from "~/src/shared/ui/common"
import { computed, onMounted, ref, watch } from "vue"
import { debounce } from "@antfu/utils"

const emits = defineEmits(["update:filters"])
const props = withDefaults(
  defineProps<{
    filtersShow: any
  }>(),
  {
    filtersShow: [
      { key: "search", options: "" },
      {
        key: "status",
        options: [
          { id: 1, name: "Status 1" },
          { id: 2, name: "Status 2" },
        ],
      },
      {
        key: "price",
        options: [
          { id: 1, name: "Price 1" },
          { id: 2, name: "Price 2" },
        ],
      },
      {
        key: "rating",
        options: [
          { id: 1, name: "Rating 1" },
          { id: 2, name: "Rating 2" },
        ],
      },
    ],
  },
)

const filters = ref({
  search: "",
  status: null,
  price: null,
  rating: null,
  date: null,
  time: null,
  city: null,
  badges: null,
})
const dateInput = ref(null)
const activeFilter = ref("")

const isFiltersOpen = ref(false)
const openFiltersToogle = () => (isFiltersOpen.value = !isFiltersOpen.value)

const makeActive = (key: string) => {
  setTimeout(() => {
    activeFilter.value = key
  }, 0)
}

const resetActive = () => {
  activeFilter.value = ""
}
const checkDesktop = () => {
  return process.client && window.innerWidth > 1024
}
const getFilterShow = (key) => {
  return props.filtersShow.find((filter) => filter.key == key)
}

const debouncedUpdateFilters = debounce(700, () => {
  emits("update:filters", filters.value)
})

watch(filters, debouncedUpdateFilters, { deep: true })

const clearFilters = () => {
  filters.value = {
    search: "",
    status: null,
    price: null,
    rating: null,
    date: null,
    time: null,
    city: null,
    badges: null,
  }
}
onMounted(() => {
  isFiltersOpen.value = checkDesktop() as boolean

  window.addEventListener("resize", () => {
    isFiltersOpen.value = checkDesktop() as boolean
  })
})
</script>

<style scoped>
input,
select,
button {
  border-radius: 0.375rem; /* Закругленные края */
}
</style>
