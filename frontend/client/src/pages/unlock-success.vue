<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta } from "#imports"

// Meta tags for the page
useHead({
  title: "Funny How – Device Unlocked",
  meta: [{ name: "description", content: "Payment successful - Device unlocking" }],
})
definePageMeta({
  layout: "error",
})
</script>

<template>
  <div>
    <div class="error flex flex-col gap-10">
      <div class="flex flex-col gap-8 text-center">
        <!-- Success Icon -->
        <div class="flex justify-center">
          <div class="w-24 h-24 rounded-full bg-green-500/20 flex items-center justify-center">
            <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
        </div>

        <!-- Main Message -->
        <div>
          <h1 class="text-5xl font-bold text-white mb-4">Payment Successful!</h1>
          <p class="text-2xl text-gray-300">Thanks for paying</p>
        </div>

        <!-- Unlock Info -->
        <div class="bg-white/10 rounded-2xl p-6 max-w-md mx-auto">
          <div class="flex items-center justify-center gap-3 mb-4">
            <svg class="w-8 h-8 text-green-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"></path>
            </svg>
            <span class="text-xl text-white font-semibold">Unlocking Device</span>
          </div>
          <p class="text-gray-300 text-lg">
            Your computer will unlock in about <span class="text-green-400 font-bold">1 minute</span>
          </p>
          <p class="text-gray-400 text-sm mt-3">
            The device checks for payment status periodically. Just wait and it will unlock automatically.
          </p>
        </div>

        <!-- Timer Info -->
        <div class="text-gray-400">
          <p class="text-sm">Device will stay unlocked for <span class="text-white font-medium">1 hour</span></p>
        </div>

        <!-- Close Instructions -->
        <div class="text-gray-500 text-sm mt-4">
          <p>You can close this page now</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.error {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}
</style>
