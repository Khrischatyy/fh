<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { IconClose } from "~/src/shared/ui/common"

const emit = defineEmits(["close"])
const modalPosition = ref(0) // Tracks the modal's vertical offset

const closePopup = () => {
  emit("close")
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === "Escape") {
    closePopup()
  }
}

const startY = ref(0)
const endY = ref(0)
const modalElement = ref<HTMLElement | null>(null) // Reference to the modal element

const disableOverflow = () => {
  if (!modalElement.value) return
  document.body.style.overflow = "hidden"
  modalElement.value.style.overflow = "hidden"
  let element = modalElement.value.parentElement
  while (element) {
    element.style.overflow = "hidden"
    element = element.parentElement
  }
}

const restoreOverflow = () => {
  if (!modalElement.value) return
  document.body.style.overflow = ""
  modalElement.value.style.overflow = ""
  let element = modalElement.value.parentElement
  while (element) {
    element.style.overflow = ""
    element = element.parentElement
  }
}

const handleTouchStart = (event: TouchEvent) => {
  startY.value = event.touches[0].clientY
  disableOverflow()
}

const handleTouchMove = (event: TouchEvent) => {
  const currentY = event.touches[0].clientY
  endY.value = currentY // Update endY on each move
  modalPosition.value = Math.max(0, currentY - startY.value)
}

const handleTouchEnd = () => {
  restoreOverflow()
  if (endY.value > startY.value + 150) {
    // Check if the swipe down is sufficient to close
    closePopup()
  } else {
    modalPosition.value = 0 // Reset modal position if not a sufficient swipe
  }
}

onMounted(() => {
  if (!props.open) return
  document.body.style.overflow = "hidden"
  window.addEventListener("keydown", handleKeyDown)
  if (props.scrollToClose) {
    window.addEventListener("touchstart", handleTouchStart)
    window.addEventListener("touchmove", handleTouchMove)
    window.addEventListener("touchend", handleTouchEnd)
  }
})

onUnmounted(() => {
  document.body.style.overflow = "auto"
  window.removeEventListener("keydown", handleKeyDown)

  if (props.scrollToClose) {
    window.removeEventListener("touchstart", handleTouchStart)
    window.removeEventListener("touchmove", handleTouchMove)
    window.removeEventListener("touchend", handleTouchEnd)
  }
})

export type PopupType =
  | "default"
  | "success"
  | "error"
  | "warning"
  | "small"
  | "medium"
  | "large"

const props = withDefaults(
  defineProps<{
    title?: string
    open: boolean
    type?: PopupType
    scrollToClose?: boolean
    modalContentClass?: string
  }>(),
  {
    title: "",
    open: false,
    type: "default",
    scrollToClose: false,
    modalContentClass: "",
  },
)
</script>

<template>
  <div
    v-if="open"
    ref="modalElement"
    class="modal backdrop-blur-[10px] overflow-hidden fixed inset-0 flex items-center justify-center p-4 sm:p-10 overflow-y-auto z-[1001]"
  >
    <div
      :class="[
        {
          'max-w-lg mx-auto': props.type == 'small',
          'max-w-3xl': props.type == 'medium',
          'max-w-6xl': props.type == 'large',
          'max-w-2xl': props.type == 'default',
        },
        props.modalContentClass || ''
      ]"
      :style="{ transform: `translateY(${modalPosition}px)` }"
      class="modal-content flex flex-col gap-5 bg-[#171717] rounded-[10px] shadow-lg w-full max-h-[90vh] p-6 relative z-20"
    >
      <div class="modal-header grid grid-cols-auto-fit items-center mb-4">
        <slot name="header" class="text-white text-[22px]/[26px] font-bold" />
        <slot name="center_header"> </slot>
        <slot class="text-right" name="action_header">
          <div class="w-full flex justify-end">
            <div
              @click="closePopup"
              class="flex flex-col justify-center w-min items-center cursor-pointer"
            >
              <IconClose />
              <span class="opacity-20">Close</span>
            </div>
          </div>
        </slot>
      </div>
      <div class="modal-body mb-10">
        <slot name="body" />
      </div>
      <div class="modal-footer w-full">
        <slot name="footer" />
      </div>
    </div>
    <div
      @click="closePopup"
      class="fixed inset-0 bg-black bg-opacity-50 z-10"
    ></div>
  </div>
</template>

<style scoped lang="scss">
.modal-content {
  width: 100%;
  margin: auto;
}
</style>
