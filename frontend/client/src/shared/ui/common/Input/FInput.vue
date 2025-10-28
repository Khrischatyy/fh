<script setup lang="ts">
import { ref, watch } from "vue"
import { IconDown } from "~/src/shared/ui/common"
import { IconSearch } from "~/src/shared/ui/common/Icon/Filter"

const props = defineProps<{
  label?: string
  modelValue: string
  type?: string
}>()

const value = ref<string>(props.modelValue)

const emit = defineEmits({
  "update:modelValue": (value: string) => true,
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  value.value = target.value
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
  <div class="w-full max-w-96 relative">
    <div
      class="relative flex items-center border border-white border-double min-h-[61px]"
    >
      <input
        @input="handleInput"
        v-model="value"
        :type="type || 'text'"
        :placeholder="label"
        class="w-full px-3 min-h-[61px] flex justify-start items-center outline-none bg-transparent text-white text-sm font-medium tracking-wide"
      />
      <span class="absolute right-[10px] cursor-pointer">
        <IconSearch />
      </span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 100%;
  max-width: 400px;
  margin: 0.5rem 0;
}
</style>
