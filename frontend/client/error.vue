<script setup lang="ts">
import {clearError, type NuxtError} from '#app'
import {Particles} from "~/src/shared/ui/components";

const props = defineProps({
  error: Object as () => NuxtError
})

const handleError = () => clearError({redirect: '/studios'})
</script>

<template>
  <div
      class="flex justify-center items-center text-white text-xxl h-full min-h-screen"
      style="height: -webkit-fill-available"
  >
    <div>
      <div class="error flex flex-col gap-10">
        <div class="text-center text-white">
          <h1 class="text-5xl font-bold">{{ error.statusCode }}</h1>
          <p class="text-2xl">Something went wrong</p>
        </div>
        <div class="flex flex-col gap-5">
          <div class="text-center text-white">
            <p class="text-xl">But we have more than 1000 studios</p>
          </div>
          <div class="flex justify-center items-center gap-2.5">
            <button
                @click="handleError"
                class="max-w-96 h-11 p-3.5 px-10 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
            >
              Check out studio near you
            </button>
          </div>
        </div>
      </div>
    </div>
    <Particles/>
  </div>
</template>