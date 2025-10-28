<template>
  <div @click.stop="copyText" class="cursor-pointer group">
    <slot></slot>
    <IconCopy
      :checked="copySuccess"
      :class="{ 'opacity-100': copySuccess, 'opacity-20': !copySuccess }"
      class="h-5 w-5 cursor-pointer group-hover:opacity-100"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { IconCopy } from "~/src/shared/ui/common"

const props = defineProps({
  textToCopy: String,
})
const copySuccess = ref(false)

const copyText = async () => {
  try {
    await navigator.clipboard.writeText(<string>props.textToCopy)
    copySuccess.value = true
    setTimeout(() => (copySuccess.value = false), 2000) // Notification visible for 2 seconds
  } catch (err) {
    console.error("Failed to copy:", err)
  }
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
