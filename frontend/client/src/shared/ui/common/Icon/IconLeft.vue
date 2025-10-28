<template>
  <svg v-if="iconType == 'bold'" width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M13 15L8 10L13 5" stroke="white" stroke-width="2"/>
  </svg>
  <svg v-if="iconType == 'thin'" width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M18.75 22.5L11.25 15L18.75 7.5" stroke="white"/>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(defineProps<{
  iconColor?: string,
  iconType?: string,
}>(), {
  iconColor: '#ffffff',
  iconType: 'bold',
})
</script>