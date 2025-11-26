<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta } from "#imports"

// Meta tags for the page
useHead({
  title: "Funny How – Payment Cancelled",
  meta: [{ name: "description", content: "Payment cancelled - Scan QR to retry" }],
})
definePageMeta({
  layout: "error",
})
</script>

<template>
  <div>
    <div class="error flex flex-col gap-10">
      <div class="flex flex-col gap-8 text-center">
        <!-- Cancel Icon -->
        <div class="flex justify-center">
          <div class="w-24 h-24 rounded-full bg-yellow-500/20 flex items-center justify-center">
            <svg class="w-12 h-12 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
          </div>
        </div>

        <!-- Main Message -->
        <div>
          <h1 class="text-5xl font-bold text-white mb-4">Payment Cancelled</h1>
          <p class="text-2xl text-gray-300">No worries, nothing was charged</p>
        </div>

        <!-- Retry Info -->
        <div class="bg-white/10 rounded-2xl p-6 max-w-md mx-auto">
          <div class="flex items-center justify-center gap-3 mb-4">
            <svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"></path>
            </svg>
            <span class="text-xl text-white font-semibold">Want to try again?</span>
          </div>
          <p class="text-gray-300 text-lg">
            Scan the <span class="text-blue-400 font-bold">QR code</span> on your device to retry payment
          </p>
          <p class="text-gray-400 text-sm mt-3">
            The QR code on the lock screen will generate a fresh payment link.
          </p>
        </div>

        <!-- Payment Method Info -->
        <div class="text-gray-400">
          <p class="text-sm">Payment is via <span class="text-green-400 font-medium">Cash App</span> only</p>
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
