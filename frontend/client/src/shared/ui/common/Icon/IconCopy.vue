<template>
  <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M25.0127 11.3984H13.7627C12.382 11.3984 11.2627 12.5177 11.2627 13.8984V25.1484C11.2627 26.5291 12.382 27.6484 13.7627 27.6484H25.0127C26.3934 27.6484 27.5127 26.5291 27.5127 25.1484V13.8984C27.5127 12.5177 26.3934 11.3984 25.0127 11.3984Z" stroke="white" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M6.2627 18.8984H5.0127C4.34965 18.8984 3.71377 18.635 3.24493 18.1662C2.77609 17.6974 2.5127 17.0615 2.5127 16.3984V5.14844C2.5127 4.4854 2.77609 3.84951 3.24493 3.38067C3.71377 2.91183 4.34965 2.64844 5.0127 2.64844H16.2627C16.9257 2.64844 17.5616 2.91183 18.0305 3.38067C18.4993 3.84951 18.7627 4.4854 18.7627 5.14844V6.39844" stroke="white" stroke-linecap="round" stroke-linejoin="round"/>
    <path v-if="checked" d="M29 12L19.375 22L15 17.4545" stroke="white" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(defineProps<{
  checked?: boolean,
}>(), {
  checked: false,
})
</script>