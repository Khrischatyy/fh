<script setup lang="ts">

import GoogleMap from "~/src/widgets/GoogleMap.vue";
import {IconNav} from "~/src/shared/ui/common";
import type {Studio} from "~/src/entities/RegistrationForms/api";

const props = defineProps<{
  isLoading?: boolean
  studio?: Studio | null
}>()

</script>

<template>
  <section class="bg-[#f7f7f7]">
    <div class="container mx-auto px-4 py-12 md:py-28">
      <div class="flex flex-col lg:flex-row items-center gap-12">
        <!-- Map Section -->
        <div class="w-full lg:w-1/2 relative">
          <div class="aspect-w-16 aspect-h-9 bg-[#f7f7f7] rounded-3xl overflow-hidden rounded-[20px]">

            <div class="w-full h-[300px] lg:h-[600px] rounded-[20px] relative">
              <a
                  :href="`https://www.google.com/maps?q=${studio?.latitude},${studio?.longitude}`"
                  target="_blank"
                  class="nav group absolute z-10 w-full h-full group bg-black cursor-pointer bg-opacity-70 hover:bg-opacity-90 transition duration-300 flex justify-center items-center"
              >
                <div
                    class="navigate-button font-[BebasNeue] group-hover:scale-115 transition duration-300 text-2xl text-white flex gap-3 justify-center items-center"
                >
                  <IconNav class="w-[20px] h-[20px]"/>
                  Direction
                </div>
              </a>
              <GoogleMap
                  class="rounded-[20px]"
                  :logo="studio?.company.logo_url"
                  :lat="studio?.latitude"
                  :lng="studio?.longitude"
              />
            </div>
          </div>
        </div>

        <!-- Contact Information -->
        <div class="w-full lg:w-1/2 flex flex-col gap-6">
          <h2 class="text-[#181818] text-4xl md:text-5xl lg:text-6xl font-black">
            It Is Easy as Google Nearest Studio
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <h3 class="text-black text-xl font-bold">Email</h3>
              <p class="text-black text-lg">studio@funny-how.com</p>
            </div>
            <div>
              <h3 class="text-black text-xl font-bold">Phone</h3>
              <p class="text-black text-lg">+1 213-887-2828</p>
            </div>
            <div>
              <h3 class="text-black text-xl font-bold">Address</h3>
              <p class="text-black text-lg">435 East 30th Street, Los Angeles, CA, 90011</p>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row gap-4 pt-10">
            <button
                class="w-full sm:w-1/2 py-6 px-4 bg-[#181818] border-4 border-[#181818] rounded-lg text-white text-xl font-bold">
              LOCK IN YOUR SESSION
            </button>
            <button
                class="w-full sm:w-1/2 py-6 px-4 rounded-lg border-4 border-[#181818] text-[#181818] text-xl font-bold">
              ADD YOUR STUDIO
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">

</style>