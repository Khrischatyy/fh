<template>
  <div
    :class="`dragdealer ${type}`"
    @mousedown="onMouseDown"
    @touchstart="onMouseDown"
  >
    <ul class="handle w-full text-center" :style="inlineStyle">
      <li
        class="w-full text-center text-xl font-[BebasNeue]"
        v-for="(item, index) in data"
        :key="index"
        :class="{ magnified: index === centerIndex }"
      >
        {{ item }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"

const props = defineProps({
  type: {
    type: String,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
  selected: {
    type: [Number, String],
    required: true,
  },
})

const emit = defineEmits(["dateChange"])

const position = ref(0)
const offset = ref(0)
let dragging = false
let previousY = 0

const setPosition = (selected) => {
  if (typeof selected === "number") {
    position.value = -(selected - 1) * 50.9
  } else {
    position.value = -props.data.indexOf(selected) * 50
  }
}

watch(
  () => props.selected,
  (newVal) => {
    setPosition(newVal)
  },
)

const onMouseDown = (event) => {
  previousY = event.touches ? event.touches[0].clientY : event.clientY
  dragging = true

  document.addEventListener("mousemove", onMouseMove)
  document.addEventListener("mouseup", onMouseUp)
  document.addEventListener("touchmove", onMouseMove)
  document.addEventListener("touchend", onMouseUp)
  emit("dragging", true)
}

const onMouseMove = (event) => {
  const clientY = event.touches ? event.touches[0].clientY : event.clientY
  offset.value = clientY - previousY

  const maxPosition = -props.data.length * 50
  position.value = Math.max(
    maxPosition,
    Math.min(50, position.value + offset.value),
  )
  previousY = event.touches ? event.touches[0].clientY : event.clientY
}

const onMouseUp = () => {
  const maxPosition = -(props.data.length - 1) * 50
  const rounderPosition =
    Math.round((position.value + offset.value * 5) / 50) * 50
  const finalPosition = Math.max(maxPosition, Math.min(0, rounderPosition))

  dragging = false
  position.value = finalPosition

  document.removeEventListener("mousemove", onMouseMove)
  document.removeEventListener("mouseup", onMouseUp)
  document.removeEventListener("touchmove", onMouseMove)
  document.removeEventListener("touchend", onMouseUp)

  const newSelected =
    props.type === "hour"
      ? -finalPosition / 50
      : props.data[-finalPosition / 50]
  emit("dateChange", props.type, newSelected)
  emit("dragging", false)
}

const inlineStyle = computed(() => ({
  willChange: "transform",
  transition: `transform ${Math.abs(offset.value) / 100 + 0.1}s`,
  transform: `translateY(${position.value}px)`,
}))

setPosition(props.selected)

// Computed property to determine the center index
const centerIndex = computed(() => {
  return Math.round(-position.value / 50)
})
</script>

<style scoped>
.dragdealer {
  position: relative;
  width: 100%;
  cursor: pointer;
}

.handle {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 50.9px;
  user-select: none;
  transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1),
    font-size 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

.magnified {
  font-size: 2.2em;
}
</style>
