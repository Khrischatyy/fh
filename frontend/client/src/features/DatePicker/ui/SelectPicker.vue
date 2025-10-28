<template>
  <div>
    <FSelect
      @change="optionChanged"
      defaultOptionIndex="0"
      placeholder="Choose Day"
      :options="options"
    />

    <div
      class="w-full focus:border-white border border-white bg-transparent text-white text-sm font-medium tracking-wide custom-transition"
      :class="[
        {
          'max-h-0 overflow-hidden opacity-0 pointer-events-none':
            selectedOption !== 'custom',
          'max-h-96 pointer-events-auto': selectedOption == 'custom',
        },
        selectedOption == 'custom' ? 'mt-5' : 'mt-0',
      ]"
    >
      <DatePicker :date="customDate" @dateChange="customDateChanged" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue"
import DatePicker from "./DatePicker.vue"
import FSelect from "~/src/shared/ui/common/Input/FSelect.vue"

const props = withDefaults(defineProps<{ timezone: string }>(), {
  timezone: "UTC",
})

const getTimezoneOffset = (timezone: string): number => {
  const currentDate = new Date()
  const localOffset = currentDate.getTimezoneOffset() * 60000 // Convert minutes to milliseconds
  const utcDate = new Date(currentDate.getTime() + localOffset)
  const targetDate = new Date(
    new Intl.DateTimeFormat("en-US", {
      timeZone: timezone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    }).format(utcDate),
  )
  return targetDate.getTime() - utcDate.getTime()
}

const getDateWithTimezone = (timezone: string): Date => {
  const offset = getTimezoneOffset(timezone)
  const dateWithOffset = new Date(new Date().getTime() + offset)
  return dateWithOffset
}

// Get today date with correct timezone
const today = getDateWithTimezone(props.timezone)
today.setHours(0, 0, 0, 0)

const tomorrow = new Date()
tomorrow.setDate(today.getDate() + 1)
tomorrow.setHours(0, 0, 0, 0)

const options = ref([
  { id: 1, name: "today", label: "Today", date: today },
  { id: 2, name: "tomorrow", label: "Tomorrow", date: tomorrow },
  { id: 3, name: "custom", label: "Another Date", date: new Date() },
])

const date = ref(today)

const optionLabels = computed(() => options.value.map((option) => option.label))
const optionNames = computed(() => options.value.map((option) => option.name))
const selectedOptionIndex = ref(0)
const selectedOptionLabel = computed(
  () => optionLabels.value[selectedOptionIndex.value],
)

const selectedOption = computed(
  () => options.value[selectedOptionIndex.value].name,
)
const customDate = ref(new Date())

const emit = defineEmits(["dateSelected"])

const optionChanged = (value) => {
  const newLabel = value.name
  const index = optionNames.value.indexOf(newLabel)
  selectedOptionIndex.value = index

  if (newLabel === "today") {
    customDateChanged("date", today)
  } else if (newLabel === "tomorrow") {
    customDateChanged("date", tomorrow)
  } else if (newLabel === "custom") {
    customDateChanged("date", new Date())
  } else {
    customDateChanged("date", new Date())
  }
}

const updateDate = () => {
  //Get Date and transform it to ISOString to pass to backend along with the timezone
  //To get clients's timezone use Intl.DateTimeFormat().resolvedOptions().timeZone;
  //Now we using address.timezone
  const selected = options.value[selectedOptionIndex.value]

  let selectedDate
  if (selected.name === "custom" && customDate.value) {
    selectedDate = customDate.value
  } else {
    selectedDate = selected.date
  }

  emit("dateSelected", { date: selectedDate.toISOString().split("T")[0] })
}

const customDateChanged = (type, newDate) => {
  customDate.value = new Date(newDate)
  updateDate()
}

watch(
  () => selectedOption,
  (newVal) => {
    if (newVal) {
      updateDate()
    }
  },
)
</script>

<style scoped>
.select-container {
  display: flex;
  padding: 0px 20px;
  overflow: hidden;
  width: 100%;
  color: #fff;
  background: transparent;
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
.option::before,
.option::after {
  content: "";
  position: absolute;
  left: 0;
  width: 100%;
  height: 50px;
  background-color: white;
  border-radius: 10px;
  opacity: 0;
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
  height: 61px;
  user-select: none;
}
</style>
