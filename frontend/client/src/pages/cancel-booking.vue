<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta, useRuntimeConfig } from "#imports"
import axios from "axios"
import { ref, onMounted, computed } from "vue"
import { useApi } from "~/src/lib/api"
import { navigateTo, useRoute } from "nuxt/app"
import { Spinner } from "~/src/shared/ui/common"

// Meta tags for the page
useHead({
  title: "Funny How – Payment Success",
  meta: [{ name: "description", content: "Processing Payment" }],
})
definePageMeta({
  layout: "error",
})

const route = useRoute()
</script>

<template>
  <div>
    <div class="error flex flex-col gap-10">
      <div class="flex flex-col gap-5">
        <div class="text-center">
          <h1 class="text-5xl font-bold">Error</h1>
          <p class="text-xl">Shit bro, something wrong with a payment</p>
        </div>
        <div class="flex justify-center items-center gap-2.5">
          <button
            @click="navigateTo('/bookings')"
            class="max-w-96 px-10 h-11 p-3.5 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            Go To My Bookings
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
