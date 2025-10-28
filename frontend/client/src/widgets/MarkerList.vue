<script setup>
import { CustomMarker } from 'vue3-google-map';
import {BrandingLogo, BrandingLogoSample, BrandingLogoSmall} from "~/src/shared/ui/branding";
import {onMounted, ref} from "vue";
import {navigateTo} from "nuxt/app";

const props = defineProps({
  marker: {
    type: Object,
    required: true,
  },
  logo: {
    type: String,
    required: true,
  },
});

const isDescriptionOpen = ref(false);

const openGoogle = (lat, lng) => {
  const url = `https://www.google.com/maps?q=${lat},${lng}`;
  window.open(url, '_blank');
}
onMounted(() => {
});
const openDescription = () => {
  isDescriptionOpen.value = !isDescriptionOpen.value;
}
</script>

<template>
  <CustomMarker
      class="flex justify-center items-center relative"
      :options="{ position: { lat: marker.lat, lng:  marker.lng }, anchorPoint: 'CENTER' }">
    <img @click="openDescription" alt="point" class="w-10" src="../shared/assets/image/studio_point.png" />
    <div v-if="isDescriptionOpen" class="p-7 min-w-48 absolute left-12 bg-neutral-900 rounded-[10px] shadow flex-col justify-center items-center gap-7 inline-flex">
      <div v-if="marker.photos" class="w-full h-20">
        <img  class="h-20 rounded-[10px] w-full object-cover" :src="marker.photos" />
      </div>
      <div class="flex-col w-full justify-start items-start gap-3.5 flex">
        <div @click="openGoogle(marker.lat, marker.lng)" class="text-white text-xl font-bold font-['Montserrat'] uppercase">{{marker.name}}</div>
        <div class="text-white text-[14px] font-normal font-['Montserrat'] tracking-wider">{{marker.street}}</div>
        <div class="text-white text-[14px] font-normal font-['Montserrat']">{{marker.operatingHours}}</div>
        <div class="text-white text-[14px] font-normal font-['Montserrat']">from {{marker.price}}$/hour</div>
        <div class="relative flex items-center cursor-pointer input border-double">
          <button @click="navigateTo(marker.url)" class="w-full px-16 py-3 font-[BebasNeue] min-h-14 flex justify-start items-center outline-none focus:border-white border border-white border-opacity-100 bg-transparent text-white text-4xl font-medium tracking-wide">
            Rent
          </button>
        </div>
      </div>
    </div>
    </CustomMarker>
</template>

<style scoped>

</style>