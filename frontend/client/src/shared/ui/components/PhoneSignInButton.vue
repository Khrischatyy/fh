<template>
  <button
    v-if="!isAuthorized"
    aria-label="Sign in with Phone"
    @click="emit('click')"
    class="flex items-center gap-3 rounded-full font-bebas p-0.5 pr-4 transition-colors duration-300 hover:bg-google-button-dark-hover border-dashed border-red"
  >
    <div class="flex items-center justify-center bg-white w-9 h-9 rounded-full">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 text-black">
        <title>Sign in with Phone</title>
        <desc>Phone Icon</desc>
        <path fill-rule="evenodd" d="M1.5 4.5a3 3 0 0 1 3-3h1.372c.86 0 1.61.586 1.819 1.42l1.105 4.423a1.875 1.875 0 0 1-.694 1.955l-1.293.97c-.135.101-.164.249-.126.352a11.285 11.285 0 0 0 6.697 6.697c.103.038.25.009.352-.126l.97-1.293a1.875 1.875 0 0 1 1.955-.694l4.423 1.105c.834.209 1.42.959 1.42 1.82V19.5a3 3 0 0 1-3 3h-2.25C8.552 22.5 1.5 15.448 1.5 6.75V4.5Z" clip-rule="evenodd" />
      </svg>
    </div>
    <span class="text-sm text-white tracking-wider font-[BebasNeue]">Sign in with Phone</span>
  </button>
</template>

<script setup lang="ts">
import { useCookie } from "#app"
import { ACCESS_TOKEN_KEY } from "~/src/lib/api/config"

const isAuthorized = useCookie(ACCESS_TOKEN_KEY).value

const emit = defineEmits<{
  click: []
}>()
</script>

<style scoped>
.font-bebas {
  font-family: 'BebasNeue', sans-serif;
}
</style>
