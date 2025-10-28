<template>
  <svg width="43" height="43" viewBox="0 0 43 43" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M11.5667 11H32.1C33.5117 11 34.6667 12.1812 34.6667 13.625V29.375C34.6667 30.8188 33.5117 32 32.1 32H11.5667C10.155 32 9 30.8188 9 29.375V13.625C9 12.1812 10.155 11 11.5667 11Z" stroke="white" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M34.6667 13.333L21.8333 22.6663L9 13.333" stroke="white" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(defineProps<{
  iconColor?: string,
}>(), {
  iconColor: '#ffffff',
})
</script>