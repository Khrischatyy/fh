<script setup lang="ts">

import {BrandingLogo} from "~/src/shared/ui/branding";
import {FSelect, IconApplePay, IconGooglePay, IconMastercard, IconVisa, Spinner} from "~/src/shared/ui/common";
import {StudioCard} from "~/src/entities/Studio";
import {useApi} from "~/src/lib/api";
import {computed, onMounted, ref} from "vue";
import {navigateTo} from "nuxt/app";

type Studio = {
  name: string
  address: string
  description: string
  hours: string
  price: number
  logo: string
  badges: string[]
  equipment: string[]
}

const props = defineProps<{
  isLoading?: boolean
  studio?: Studio | null
}>()

const countries = [{label: 'United States', value: 'us'}];
const cities = [{label: 'Los Angeles', value: 'la'}, {label: 'New York', value: 'ny'}];
const days = [{label: 'Today', value: 'today'}, {label: 'Tomorrow', value: 'tomorrow'}];
const times = [{label: '12:00 AM 1 SEP', value: '12am'}, {label: '01:00 AM 1 SEP', value: '1am'}];

const city = ref('la')

const selectedStudio = computed(() => {
  return cities.find((c) => c.value === city.value)
})

const goToStudio = (studio) => {
  navigateTo(`/@${studio?.slug}`)
}

</script>

<template>
  <div class="bg-[#181818] text-white">
    <div class="container bg-[#181818] mx-auto">
      <!-- Hero Section -->
      <section class="grid grid-cols-1 lg:grid-cols-2">
        <div class="w-full px-4 py-16 flex flex-col justify-between items-center lg:items-start">
          <BrandingLogo class="mb-6" size="superLarge"/>
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-black mb-6 text-center lg:text-left">All In One Booking
            Solution For
            Recording
            Studios</h1>
          <p class="text-xl opacity-50 mb-8">Secure Your Revenue: Avoid cancellations and no-shows by requiring payments
            before booking.</p>
          <div class="flex flex-col w-full sm:flex-row gap-4">
            <button class="bg-[#f7931e] text-white font-bold py-4 px-8 rounded-lg text-xl">Connect your studio</button>
            <button class="bg-white text-black font-bold py-4 px-8 rounded-lg text-xl">Find Your Studio</button>
          </div>
        </div>
        <div class="w-full px-4 py-16 lg:px-16 lg:py-16 bg-[#0f0e0e] h-full rounded-lg relative">
          <h2 class="text-4xl md:text-5xl lg:text-6xl font-black mb-8">Lock In Your Session With Ease</h2>
          <div class="space-y-6">
            <div class="flex flex-col sm:flex-row gap-4">
              <FSelect :options="countries"
                       class="w-full sm:w-1/2 z-[104]"/>
              <FSelect :options="cities"
                       v-model="city"
                       model-key="value"
                       class="w-full sm:w-1/2 z-[103]"/>

            </div>
            <div class="flex flex-col sm:flex-row gap-4">
              <div class="min-w-[352px]">
                <p class="text-2xl font-[BebasNeue]">Found studio in {{ selectedStudio.label }}:</p>
                <StudioCard v-if="studio"
                            @click="goToStudio(studio)"
                            theme="grey"
                            main-color="#191919"
                            class="border-dashed border-2 border-opacity-50 hover:border-opacity-100 max-w-[22rem] cursor-pointer zoom-effect bg-[#191919]"
                            :studio="studio"/>
              </div>
              <div class="flex w-full flex-col gap-5">
                <FSelect :options="days"
                         class="w-full z-[102]"/>
                <FSelect :options="times"
                         class="w-full z-[101]"/>
                <FSelect :options="times"
                         class="w-full z-[100]"/>
                <div class="flex justify-between">
                  <span class="font-['BebasNeue'] text-3xl">PRICE:</span>
                  <span class="font-['BebasNeue'] text-3xl">$100</span>
                </div>
                <div class="flex justify-center items-center flex-col gap-2">
                  <div
                      class="text-white opacity-70 text-sm font-normal font-['Montserrat'] tracking-wide"
                  >
                    We accept
                  </div>
                  <div class="justify-center items-center flex gap-5 mb-10">
                    <IconApplePay/>
                    <IconGooglePay/>
                    <IconVisa/>
                    <IconMastercard/>
                  </div>
                </div>
                <div
                    class="relative w-full flex items-center m-auto cursor-pointer max-w-[211px] input border border-white border-double"
                >
                  <button
                      class="w-full px-3 h-11 font-['BebasNeue'] flex justify-center items-center outline-none bg-transparent text-white text-2xl text-center font-medium tracking-wide"
                  >
                    Book Now
                  </button>
                </div>
              </div>
            </div>
            <Spinner :is-loading="isLoading"/>

          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped lang="scss">

</style>