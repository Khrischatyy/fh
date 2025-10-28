<script setup lang="ts">
import { IconDown } from "~/src/shared/ui/common"
import { ref, watch } from "vue"

const props = defineProps<{
  label?: string
  placeholder?: string
  options: { id: number | string; name: string }[]
  modelValue: string | number | null
  size?: "sm" | "md" | "lg"
  thin?: boolean
  wide?: boolean
  error?: string | boolean
}>()

const value = ref<string | number | null>(props.modelValue)

const emit = defineEmits({
  change: (value: string | number) => true,
  "update:modelValue": (value: string | number) => true,
})

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  value.value = target.value
  emit("change", target.value)
  emit("update:modelValue", target.value)
}

watch(
  () => props.modelValue,
  (newValue) => {
    value.value = newValue
  },
)
</script>

<template>
  <div :class="wide ? 'max-w-full' : 'max-w-96'" class="w-full relative">
    <div
      :class="label ? 'mb-1.5' : 'mb-0'"
      class="label-action grid grid-cols-[max-content,max-content] justify-between items-center w-full"
    >
      <div
        v-if="label"
        :class="{
          'opacity-20': props.size === 'sm',
          'opacity-100': props.size === 'md' || props.size === 'lg',
        }"
        class="text-white text-sm font-normal tracking-wide"
      >
        {{ label }}
      </div>
      <div
        v-if="error"
        class="text-right text-red-500 text-sm font-normal tracking-wide"
      >
        {{ error }}
      </div>
    </div>
    <div class="flex items-center">
      <select
        @change="handleChange"
        v-model="value"
        class="opacity-0 absolute top-0 cursor-pointer h-full w-full outline-none focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
        name="workday"
      >
        <option value="" disabled>Choose {{ props.label }}</option>
        <option
          v-for="option in props.options"
          :key="option.id"
          :value="option.id"
        >
          {{ option.name }}
        </option>
      </select>
    </div>
    <div class="relative flex items-center pointer-events-none">
      <div
          :class="thin ? 'h-10' : 'h-11'"
        class="w-full flex justify-start items-center gap-2 px-3 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 hover:border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide"
      >
        <slot name="icon" />
        {{
          props.options.find((option) => option.id == value)?.name ||
          props.placeholder
        }}
      </div>
      <span class="absolute right-0 cursor-pointer">
        <IconDown />
      </span>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
