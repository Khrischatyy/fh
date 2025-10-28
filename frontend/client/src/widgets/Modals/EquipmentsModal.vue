<script setup lang="ts">
import defaultLogo from "~/src/shared/assets/image/studio.png"
import { Popup } from "~/src/shared/ui/components"
import { getStatus, getColor, getRatingColor } from "~/src/shared/utils"
import { computed, inject, onMounted, onUnmounted, ref } from "vue"
import {
  IconBackDraw,
  IconDown,
  IconLike,
  IconMic,
} from "~/src/shared/ui/common"
import IconStar from "~/src/shared/ui/common/Icon/IconStar.vue"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common/Spinner"
import type { AddressFull } from "~/src/entities/Studio/api"

const props = withDefaults(
  defineProps<{
    showPopup: boolean
  }>(),
  {
    showPopup: false,
  },
)
const isLoading = ref(false)
const address = inject("address") as AddressFull | undefined
const emit = defineEmits<{
  (e: "togglePopup"): void
  (e: "closePopup"): void
}>()

const categorizedEquipments = computed(() => {
  return address.value?.equipments.reduce((acc, equipment) => {
    const type = equipment.type.name
    if (!acc[type]) {
      acc[type] = []
    }
    acc[type].push(equipment)
    return acc
  }, {})
})
const openCategories = ref({})

const toggleCategory = (type) => {
  openCategories.value[type] = !openCategories.value[type]
}

const openAllCategories = () => {
  Object.keys(categorizedEquipments.value).forEach((type) => {
    openCategories.value[type] = true
  })
}

onMounted(() => {
  const firstCategory = Object.keys(categorizedEquipments.value)[0]
  if (firstCategory) {
    openCategories.value[firstCategory] = true
  }
})

const closePopup = () => {
  emit("closePopup")
}
</script>

<template>
  <Popup
    :scroll-to-close="true"
    type="medium"
    :title="'Equipments'"
    :open="showPopup"
    @close="closePopup"
  >
    <template #header>
      <div class="flex justify-start items-center gap-5">
        <div>
          <div
            @click="openAllCategories"
            class="text-4xl font-bold cursor-pointer select-none font-['BebasNeue'] text-darkred"
          >
            Equipments
          </div>
        </div>
      </div>
    </template>
    <template #center_header>
      <div
        class="text-white text-center text-4xl hidden md:block font-bold font-['BebasNeue']"
      >
        {{ address?.company.name }}
      </div>
    </template>
    <template #action_header>
      <div class="text-white text-4xl text-right font-bold hover:opacity-70">
        <button @click="closePopup">
          <IconBackDraw />
        </button>
      </div>
    </template>
    <template #body>
      <div class="flex flex-col gap-7 justify-start items-start relative">
        <Spinner :is-loading="isLoading" />
        <div class="equipment-list">
          <div
            v-for="(equipments, type) in categorizedEquipments"
            :key="type"
            class="equipment-category"
          >
            <div
              @click="toggleCategory(type)"
              class="flex gap-3 cursor-pointer hover:opacity-70"
            >
              <IconMic class="w-6" />
              <img
                :src="equipments[0].type.icon"
                alt="icon"
                class="equipment-icon hidden"
              />
              <div class="text-white font-['BebasNeue'] text-3xl">
                {{ type.toUpperCase() }}:
              </div>
              <span class="arrow text-white">
                <IconDown :rotation="openCategories[type] ? 180 : 0" />
              </span>
            </div>
            <ul
              :class="{
                'max-h-0 overflow-hidden': !openCategories[type],
                'max-h-96': openCategories[type],
              }"
              class="ml-6 pl-3 mt-3 mb-6 custom_transition"
            >
              <li
                v-for="(equipment, index) in equipments"
                :key="equipment.id"
                class="equipment-item text-xl mb-4"
              >
                <span class="text-white font-['BebasNeue']"
                  >{{ index + 1 }}.
                </span>
                <span class="text-darkred font-['BebasNeue']">{{
                  equipment.name
                }}</span>
                <span
                  class="text-white font-['BebasNeue']"
                  v-if="equipment.description"
                  >: {{ equipment.description }}</span
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div
        v-if="address?.equipments.length > 0"
        class="relative flex items-center m-auto cursor-pointer max-w-[211px] input border border-white border-double"
      >
        <button
          @click="closePopup"
          class="w-full px-3 h-11 font-['BebasNeue'] flex justify-center items-center outline-none bg-transparent text-white text-2xl text-center font-medium tracking-wide"
        >
          Close
        </button>
      </div>
    </template>
  </Popup>
</template>

<style scoped lang="scss">
.custom_transition {
  transition: max-height 0.3s ease-in-out;
}
</style>
