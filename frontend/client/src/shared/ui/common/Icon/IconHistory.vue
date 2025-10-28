<template>
  <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M17.5 18.75L12.5 23.75L17.5 28.75" stroke="white"/>
    <path d="M7.42228 19.375C6.45919 17.7069 6.07344 15.7676 6.32486 13.8579C6.57627 11.9482 7.4508 10.1748 8.81282 8.81282C10.1748 7.4508 11.9482 6.57627 13.8579 6.32486C15.7676 6.07344 17.7069 6.45919 19.375 7.42228C21.0431 8.38536 22.3468 9.87197 23.0839 11.6515C23.8211 13.4311 23.9504 15.4041 23.4519 17.2647C22.9533 19.1252 21.8548 20.7693 20.3267 21.9418C18.7985 23.1144 16.9262 23.75 15 23.75" stroke="white" stroke-linecap="round"/>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(defineProps<{
  iconColor?: string,
}>(), {
  iconColor: '#ffffff',
})
</script>