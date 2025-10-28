<script setup lang="ts">
import { onMounted, ref, useSlots, watch } from "vue"
import { IconUpload } from "~/src/shared/ui/common"

const props = withDefaults(
  defineProps<{
    label?: string
    placeholder?: string
    modelValue?: string | number | null
    type?: string
    size?: "sm" | "md" | "lg"
    wide?: boolean
    error?: string | boolean
    success?: string | boolean
    inputStyle?: "plain" | "classic"
    disabled?: boolean
  }>(),
  {
    size: "md",
    inputStyle: "classic",
  },
)
const slots = useSlots()
const value = ref<string | number | null>(props.modelValue)
const file = ref<File | null>(null)
const imageUrl = ref<string | null>(null)

const emit = defineEmits({
  "update:modelValue": (value: string | number | File) => true,
  blur: (event: Event) => true,
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (props.type === "file" && target.files) {
    file.value = target.files[0]
    imageUrl.value = URL.createObjectURL(target.files[0])
    emit("update:modelValue", target.files[0])
  } else {
    value.value = target.value
    emit("update:modelValue", target.value)
  }
}
const handlePlaceholderClick = () => {
  const fileInput = document.getElementById("fileInput") as HTMLInputElement
  fileInput.click()
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (props.type !== "file") {
      value.value = newValue
    }
  },
)
</script>

<template>
  <div :class="wide ? 'max-w-full' : 'max-w-96'" class="w-full flex-col flex">
    <div
      :class="label ? 'mb-1.5' : 'mb-0'"
      class="label-action grid grid-cols-[max-content,auto] justify-between items-center w-full"
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
        class="text-right text-red-500 text-sm font-normal tracking-wide mb-1.5"
      >
        {{ error }}
      </div>
      <div
        v-if="success"
        class="text-right text-green text-sm font-normal tracking-wide mb-1.5"
      >
        {{ success }}
      </div>
      <div
        v-if="slots?.action"
        class="action flex justify-end items-center w-full"
      >
        <slot name="action" />
      </div>
    </div>
    <div
      :class="{ 'w-full h-full': inputStyle == 'plain' }"
      class="relative flex items-center justify-center"
    >
      <div class="absolute left-3">
        <slot name="icon" />
      </div>
      <input
        v-if="props.type !== 'file'"
        v-bind="$attrs"
        :disabled="disabled"
        @input="handleInput"
        @blur="$emit('blur', $event)"
        v-model="value"
        :placeholder="props.placeholder"
        :class="{
          'text-opacity-20': disabled,
          'pl-10': slots?.icon,
          'border-red': error,
          'border-white': !error && !slots?.icon,
          'py-3 h-[44px]': props.size === 'sm',
          'py-5': props.size === 'md',
          'py-7': props.size === 'lg',
        }"
        class="w-full flex justify-start items-center px-3 h-11 outline-none rounded-[10px] focus:border-white border border-opacity-20 border-white focus:border-opacity-100 bg-transparent text-white text-sm font-medium tracking-wide"
        :type="props.type || 'text'"
      />
      <div
        v-else
        :class="{
          'border border-white border-opacity-20 rounded-[10px]':
            inputStyle == 'classic',
          'rounded-full': inputStyle == 'plain',
        }"
        class="w-full h-full flex items-center justify-center rounded-[10px] bg-transparent text-white text-sm font-medium tracking-wide cursor-pointer"
        @click="handlePlaceholderClick"
      >
        <input
          id="fileInput"
          v-bind="$attrs"
          type="file"
          class="hidden"
          :class="{
            'pl-10': slots?.icon,
            'border-red': error,
            'border-white': !error && !slots?.icon,
          }"
          @change="handleInput"
        />
        <span
          v-if="!imageUrl"
          :class="{ 'opacity-20': inputStyle == 'classic' }"
        >
          <IconUpload />
        </span>
        <img
          v-if="imageUrl"
          :src="imageUrl"
          :class="{
            'rounded-[10px]': inputStyle == 'classic',
            'rounded-full': inputStyle == 'plain',
          }"
          alt="Uploaded Image"
          class="w-full h-full object-cover"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
