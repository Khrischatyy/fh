<template>
  <div
    :class="`border-${borderColor} border-opacity-${borderOpacity}`"
    class="p-[10px] text-white rounded-[10px] h-full flex opacity-70 hover:opacity-100 items-center justify-center border border-dashed cursor-pointer"
  >
    <div
        :class="{'flex': type === 'room', 'flex-col': type === 'studio'}"
        class="flex justify-center gap-1 items-center">
      <IconAddRing
          :class="{'h-10 w-10': type === 'room', 'h-20 w-20': type === 'studio'}"
      />
      <span
          :class="{'text-sm': type === 'room', 'text-2xl': type === 'studio'}"
          class="text-center">{{ props.title }}</span>
      <span v-if="props.subtitle" class="text-sm text-neutral-700">{{ props.subtitle }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
// No additional logic needed for now
import { IconAddRing } from "~/src/shared/ui/common"
const props = withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
    borderColor?: string
    borderOpacity?: string
    type?: string
  }>(),
  {
    title: "Add Studio",
    borderColor: "white",
    borderOpacity: "20",
    type: "studio",
  },
)
</script>

<style scoped>
.border-dashed {
  border-width: 2px;
  border-style: dashed;
}
.m-10 {
  margin: 10px;
}
</style>
