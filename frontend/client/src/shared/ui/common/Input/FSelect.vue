<script setup lang="ts">
import {IconDown} from "~/src/shared/ui/common"
import {computed, onMounted, ref, watch} from "vue"

export type OptionType = {
  id: number | string
  name: string
  label: string
}
const props = defineProps<{
  label?: string
  placeholder?: string
  options: { id: number | string; name: string; label: string }[]
  modelValue?: string | number | null
  size?: "sm" | "md" | "lg"
  error?: string | boolean
  modelKey?: string
  scroll?: boolean
  defaultOptionIndex?: string
}>()

const value = ref<string | number | null>(props.modelValue)

const emit = defineEmits({
  change: (value: string | number) => true,
  "update:modelValue": (value: string | number) => true,
})

onMounted(() => {
  //Подумать над тем как дефолтное значение передавать.
  //Assign default value if needed
  // if (props.defaultOptionIndex) {
  //   handleChange(props.options[parseInt(props.defaultOptionIndex)])
  // }
})

const handleChange = (option: OptionType) => {
  // Use option.id for value if modelKey is provided, otherwise use the entire option object
  value.value = props.modelKey ? option[props.modelKey] : option
  emit("change", value.value)
  emit("update:modelValue", value.value)
  showOptions.value = false
}

const showOptions = ref(false)
const toggleDropdown = () => {
  showOptions.value = !showOptions.value
}

watch(
    () => props.modelValue,
    (newValue) => {
      value.value = newValue
    },
)

const valueShow = computed(() => {
  if (props.modelKey) {
    return (
        props.options.find((option) => option[props.modelKey] == value.value)
            ?.label || props.placeholder
    )
  }

  // If value is an object, compare option.id with value.id
  if (typeof value.value === "object" && value.value !== null) {
    return value.value.label || props.placeholder
  }

  return (
      props.options.find((option) => option.id == value.value)?.label ||
      props.placeholder
  )
})

const optionsContainer = ref<HTMLElement | null>(null)
const optionsChoose = ref<HTMLElement | null>(null)
watch(showOptions, (newValue) => {
  if (newValue) {
    optionsContainer.value.classList.add("max-h-64")
    optionsContainer.value.classList.remove("opacity-100")
    optionsChoose.value.classList.add("border-b")
    optionsChoose.value.classList.remove("border-double")
    setTimeout(() => {
      optionsContainer.value.classList.add("opacity-100")
    }, 300) // Match the duration of the max-height transition
  } else {
    optionsContainer.value.classList.remove("max-h-64")
    optionsContainer.value.classList.remove("opacity-100")
    setTimeout(() => {
      optionsChoose.value.classList.add("border-double")
      optionsChoose.value.classList.remove("border-b")
    }, 100) // Match the duration of the max-height transition
  }
})
</script>
<template>
  <div
      :class="{
      'w-full': props.size === 'lg',
      'w-72': props.size === 'md',
      'w-52': props.size === 'sm',
    }"
      class="w-full max-w-96 relative"
  >
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
    <div class="relative">
      <div
          ref="optionsChoose"
          :class="['relative w-full flex items-center', showOptions ? '' : '']"
          class="h-[61px] cursor-pointer border-white border-double border-t border-l border-r pr-9"
          @click="toggleDropdown"
      >
        <div
            class="w-full whitespace-nowrap overflow-hidden flex border-right justify-start items-center gap-2 px-3 min-h-[61px] h-full outline-none bg-transparent text-white font-[BebasNeue] text-2xl font-medium tracking-wide"
        >
          <slot name="icon"/>
          {{ valueShow }}
        </div>
        <span class="absolute -right-[1px] mr-2 mb-1 cursor-pointer">
          <IconDown :rotation="showOptions ? 180 : 0"/>
        </span>
      </div>
      <div
          ref="optionsContainer"
          :class="[
          'select-options',
          showOptions ? 'max-h-64 border-t mt-3' : 'max-h-0 ',
          scroll ? 'overflow-y-auto' : 'overflow-hidden',
        ]"
          class="select-options custom-transition absolute top-full left-0 border-l border-r border-b border-white h-auto w-full bg-black"
      >
        <ul class="w-full h-full">
          <li
              v-if="props.options.length === 0"
              class="option cursor-pointer text-2xl hover:opacity-60 py-4"
          >
            <div class="w-full h-full flex items-center justify-center px-5">
              <div
                  class="text-white text-left font-[BebasNeue] font-medium tracking-wide w-full"
              >
                No options available
              </div>
            </div>
          </li>
          <template :key="option.name" v-for="(option, index) in props.options">
            <li
                @click="handleChange(option)"
                class="option cursor-pointer text-2xl hover:opacity-60 py-4"
            >
              <div class="w-full h-full flex items-center justify-center px-5">
                <div
                    class="text-white text-left font-[BebasNeue] font-medium tracking-wide w-full"
                >
                  {{ option.label }}
                </div>
              </div>
            </li>
            <div
                v-if="index != props.options.length - 1"
                class="border-b border-white mx-5"
            ></div>
          </template>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.custom-transition {
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

.border-right {
  position: relative;
}

.border-right::after {
  content: "";
  position: absolute;
  right: 0;
  margin-bottom: 7px;
  width: 1px;
  height: 50%;
  background-color: rgb(255, 255, 255);
}
</style>
