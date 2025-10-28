<template>
  <div :class="open ? 'py-51' : ''" class="time-picker gap-2">
    <CustomWheel
      @touchstart="preventTouch"
      @touchmove="preventTouch"
      @touchend="preventTouch"
      type="hour"
      :data="hours"
      :selected="selectedHour"
      @dateChange="hourChanged"
    />
    <CustomWheel
      @touchstart="preventTouch"
      @touchmove="preventTouch"
      @touchend="preventTouch"
      type="period"
      :data="periods"
      :selected="selectedPeriod"
      @dateChange="periodChanged"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, watchEffect } from "vue"
import { CustomWheel } from "~/src/features/CustomWheel"
import { useRoute } from "nuxt/app"

const props = defineProps<{
  time?: string
  open?: boolean
  rentingForm?: Record<string, any> // Adjust the type according to your actual rentingForm structure
  availableHours?: availableHourType[]
}>()

type availableHourType = { time: string; date: string; iso_string: string }

const processedHour = ref(0)
const preventTouch = (event) => {
  event.preventDefault()
}

const emit = defineEmits(["timeChange"])
const periods = ref(["AM", "PM"])
const selectedHour = ref(0)
const selectedPeriod = ref("AM")
const dragging = (isDragging) => {
  emit("dragging", isDragging)
}

watch(
  () => props.time,
  (newTime) => {
    const hour = parseInt(newTime?.split(":")[0])
    selectedHour.value = hour % 12 || 12
    selectedPeriod.value = hour >= 12 ? "PM" : "AM"
  },
)

const hours = computed(() => processAvailableHours())

function processAvailableHours() {
  const amHours = new Set()
  const pmHours = new Set()

  props.availableHours.forEach((time) => {
    const hour = parseInt(time.time.split(":")[0])
    if (hour < 12) {
      amHours.add(hour % 12 || 12)
    } else {
      pmHours.add(hour % 12 || 12)
    }
  })
  // Update periods based on available hours
  if (amHours.size === 0) periods.value = ["PM"]
  else if (pmHours.size === 0) periods.value = ["AM"]
  else periods.value = ["AM", "PM"]

  return Array.from(new Set([...amHours, ...pmHours])).map((hour) =>
    hour.toString().padStart(2, "0"),
  )
}

watch(
  () => props.availableHours,
  (newHours) => {
    if (hours.value.length > 0) {
      selectedHour.value = hours.value[0]
      selectedPeriod.value = periods.value.includes("AM")
        ? parseInt(hours.value[0]) < 12
          ? "AM"
          : "PM"
        : "PM"
      emit("timeChange", props.availableHours[0].time)
    }
  },
)

const hourChanged = (type, changedDataIndex) => {
  const hour = props.availableHours[changedDataIndex].time
  const hourPart = parseInt(hour.split(":")[0])

  // Ensure processedHour is in 12-hour format
  processedHour.value = hourPart % 12 || 12

  emit("timeChange", formatTime(processedHour.value, selectedPeriod.value))
}

const periodChanged = (type, changedData) => {
  selectedPeriod.value = changedData

  emit("timeChange", formatTime(processedHour.value, selectedPeriod.value))
}

const formatTime = (hour, period) => {
  let formattedHour
  let [hourPart] = hour.toString().split(":").map(Number)

  if (period === "AM") {
    // If it's 12 AM (midnight), set the formattedHour to 0
    formattedHour = hourPart === 12 ? 0 : hourPart
  } else {
    // If it's 12 PM (noon), keep the formattedHour as 12
    // For other PM hours, add 12 to convert to 24-hour format
    formattedHour = hourPart === 12 ? 12 : hourPart + 12
  }

  return `${formattedHour.toString().padStart(2, "0")}:00`
}
</script>

<style scoped>
.time-picker {
  display: flex;
  padding: 0px 20px;
  margin: 30px 0;
  overflow: hidden;
  width: 100%;
  color: #fff;
  background: transparent;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

.hour,
.period,
.option {
  position: relative;
  height: 50px;
  margin: 0;
}

.hour::before,
.hour::after,
.period::before,
.period::after,
.option::before {
  content: "";
  position: absolute;
  left: 0;
  width: 100%;
  height: 50px;
  background-color: white;
  opacity: 0;
  border-radius: 10px;
  pointer-events: none;
  z-index: 1;
}

.hour::before,
.period::before,
.option::before {
  top: -51px;
}

.hour::after,
.period::after,
.option::after {
  bottom: -51px;
}

li {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 20px;
  user-select: none;
}
.py-51 {
  padding: 51px 0;
}
</style>
