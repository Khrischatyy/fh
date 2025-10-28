<template>
  <svg width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="10.5" cy="5.87447" r="3.30025" :stroke="iconColor" stroke-linecap="round"/>
    <path d="M5.20216 14.4752C5.7463 12.6601 7.54416 11.6504 9.43907 11.6504H11.561C13.4559 11.6504 15.2538 12.6601 15.7979 14.4752C16.0092 15.1798 16.1832 15.9645 16.2481 16.7664C16.2776 17.1298 15.98 17.4258 15.6154 17.4258H5.38466C5.02012 17.4258 4.72251 17.1298 4.75194 16.7664C4.81688 15.9645 4.99093 15.1798 5.20216 14.4752Z" :stroke="iconColor" stroke-linecap="round"/>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(defineProps<{
  iconColor?: string,
}>(), {
  iconColor: '#ffffff',
})
</script>