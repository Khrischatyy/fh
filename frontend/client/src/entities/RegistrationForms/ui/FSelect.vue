<script setup lang="ts">
import { IconDown } from "~/src/shared/ui/common";
import { ref, watch } from "vue";

const props = defineProps<{
  label?: string
  options: {
    id: number,
    name: string
  }[]
  modelValue: string | null
}>()

const value = ref<string | null>(props.modelValue)

const emit = defineEmits({
  change: (value: string) => true,
  'update:modelValue': (value: string) => true
})

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  value.value = target.value
  emit('change', target.value)
  emit('update:modelValue', target.value)
}

watch(() => props.modelValue, (newValue) => {
  value.value = newValue
})
</script>

<template>
  <div class="w-full min-w-64 sm:min-w-80 max-w-96 relative">
    <div class="flex items-center">
      <select @change="handleChange" v-model="value" class="opacity-0 absolute top-0 cursor-pointer h-full w-full outline-none focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide" name="workday">
        <option value="" disabled>Choose {{ props.label }}</option>
        <option v-for="option in props.options" :key="option.id" :value="option.id">{{ option.name }}</option>
      </select>
    </div>
    <div class="relative flex items-center pointer-events-none input border-double">
      <div class="w-full px-3 h-11 flex justify-start items-center outline-none focus:border-white border border-white border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide">
        {{ props.options.find(option => option.id === Number(value))?.name || props.label }}
      </div>
      <span class="absolute right-0 cursor-pointer">
        <IconDown/>
      </span>
    </div>
  </div>
</template>