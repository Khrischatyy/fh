<script setup lang="ts">

import {ArtistSection, HeroSection, HomescreenSection, MapSection, StudioSection} from "~/src/pages/welcome/sections";
import {useApi} from "~/src/lib/api";
import {onMounted, ref} from "vue";

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

const studio = ref<Studio | null>(null)
const isLoading = ref(true)
const getMyStudios = async () => {
  const {fetch} = useApi<any>({
    url: `random-studio`,
    auth: true
  })
  isLoading.value = true

  await fetch().then((res) => {
    studio.value = res.data
    console.log(res.data)
  }).finally(() => {
    isLoading.value = false
  });
}


onMounted(() => {
  getMyStudios()
})
</script>

<template>
  <div>
    <HeroSection :is-loading="isLoading" :studio="studio"/>
    <MapSection :is-loading="isLoading" :studio="studio"/>
    <ArtistSection/>
    <StudioSection/>
    <HomescreenSection/>
  </div>
</template>

<style scoped lang="scss">
h1 {
  color: red;
}
</style>