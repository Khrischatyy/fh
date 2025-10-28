<script setup lang="ts">
import { definePageMeta } from "#imports"
import { navigateTo } from "nuxt/app"

definePageMeta({
  layout: "error",
})
</script>

<template>
  <div>
    <div class="error flex flex-col gap-10">
      <div class="text-center">
        <h1 class="text-5xl font-bold">404</h1>
        <p class="text-2xl">Page not found</p>
      </div>
      <div class="flex flex-col gap-5">
        <div class="text-center">
          <p class="text-xl">But we have more than 1000 studios</p>
        </div>
        <div class="flex justify-center items-center gap-2.5">
          <button
            @click="navigateTo('/studios')"
            class="max-w-96 h-11 p-3.5 px-10 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            Check out studio near you
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
