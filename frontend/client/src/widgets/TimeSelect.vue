<template>
  <div class="relative w-full">
    <FSelect
      :key="props.availableHours[0].iso_string"
      :placeholder="placeholder"
      :options="structuredHours"
      :value="time"
      @change="timeChanged($event)"
      :scroll="true"
      class="w-full border-double focus:border-white border border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
    ></FSelect>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, computed, watch } from "vue"
import FSelect, { type OptionType } from "../shared/ui/common/Input/FSelect.vue"
import { isoToHumanReadable } from "../shared/utils"

type AvailbleHourType = {
  time: string
  iso_string: string
}

const props = withDefaults(
  defineProps<{
    rentingForm: any
    label: string
    placeholder: string
    time?: string
    availableHours?: AvailbleHourType[]
  }>(),
  {
    label: "Time",
    time: "09:00",
    placeholder: "Choose Time",
    rentingForm: {},
  },
)

const emit = defineEmits(["timeChanged"])
const structuredHours = computed(() => {
  const hours = props.availableHours?.map((hour, index) => {
    return {
      id: index + 1,
      label: hour.time,
      name: hour.iso_string,
    }
  })
  return hours
})

const timeChanged = (value: OptionType) => {
  emit("timeChanged", isoToHumanReadable(value.name))
}
</script>

<style scoped></style>
