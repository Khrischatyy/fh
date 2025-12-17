<script setup lang="ts">
import { useToastStore } from '~/src/shared/stores/useToastStore'
import { computed } from 'vue'

const toastStore = useToastStore()

const typeClasses = computed(() => {
  const classes: Record<string, string> = {
    error: 'bg-red-600 text-white',
    success: 'bg-green-600 text-white',
    warning: 'bg-yellow-500 text-black',
    info: 'bg-blue-600 text-white',
  }
  return classes[toastStore.type] || classes.error
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div
        v-if="toastStore.isVisible"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[9999] max-w-md w-full px-4"
      >
        <div
          :class="[
            'px-4 py-3 rounded-lg shadow-lg flex items-center justify-between gap-3',
            typeClasses
          ]"
        >
          <span class="text-sm font-medium">{{ toastStore.message }}</span>
          <button
            @click="toastStore.hide()"
            class="shrink-0 hover:opacity-70 transition-opacity"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
