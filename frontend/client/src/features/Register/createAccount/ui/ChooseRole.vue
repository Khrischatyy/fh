<template>
  <div>
    <div class="flex-col w-full justify-start items-start gap-1.5 flex">
      <div class="w-full justify-between items-start inline-flex">
        <div class="text-white text-sm font-normal tracking-wide">
          Your role
        </div>
        <div
          class="hidden text-right text-red-500 text-sm font-normal tracking-wide"
        >
          Error message
        </div>
      </div>
      <div class="justify-start items-center w-full gap-2.5 inline-flex">
        <button
          @click="updateField('user')"
          :class="
            selectedRole === 'user' ? 'bg-white text-neutral-900' : 'text-white'
          "
          class="w-full h-11 p-3.5 hover:opacity-90 rounded-[10px] border text-sm font-medium tracking-wide flex items-center justify-center"
        >
          <icon-user
            :icon-color="selectedRole === 'user' ? '#171717' : '#ffffff'"
            class="w-4 h-4 mr-2"
          />
          Artist
        </button>
        <button
          @click="updateField('studio_owner')"
          :class="
            selectedRole === 'studio_owner'
              ? 'bg-white text-neutral-900'
              : 'text-white'
          "
          class="w-full h-11 p-3.5 hover:opacity-90 rounded-[10px] border text-sm font-medium tracking-wide flex items-center justify-center"
        >
          <icon-mic
            :icon-color="
              selectedRole === 'studio_owner' ? '#171717' : '#ffffff'
            "
            class="w-4 h-4 mr-2"
          />
          Studio Owner
        </button>
      </div>
    </div>
    <div
      class="max-w-96 h-11 p-3.5 justify-between items-center gap-2.5 inline-flex"
    >
      <button
        @click="navigateBack('auth')"
        class="w-full flex justify-center items-center h-11 p-3.5 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
      >
        <icon-left />
        Return Back
      </button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { type PropType, ref } from "vue"
import { IconLeft, IconMic, IconUser } from "~/src/shared/ui/common"

const props = defineProps({
  selectedRole: {
    type: String,
    default: "",
  },
})

const emit = defineEmits(["updateRole", "navigateBack"])

const updateField = (role: string) => {
  emit("updateRole", role)
}

const navigateBack = ($event: string) => {
  emit("navigateBack", $event)
}
</script>

<style lang="scss" scoped></style>
