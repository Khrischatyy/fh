<template>
  <svg viewBox="0 0 31 31" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M23 7.58594L8 22.5859"
      stroke="white"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M8 7.58594L23 22.5859"
      stroke="white"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    iconColor?: string
    iconType?: string
  }>(),
  {
    iconColor: "#ffffff",
    iconType: "bold",
  },
)
</script>
