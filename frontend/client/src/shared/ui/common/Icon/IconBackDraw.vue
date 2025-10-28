<template>
  <svg
    width="40"
    height="40"
    viewBox="0 0 40 40"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M9 17.5L4.5 12M4.5 12L9 6.5M4.5 12H23.738C24.5768 12 25.4131 12.0918 26.2319 12.2738L26.8405 12.409C28.5774 12.795 30.1683 13.6683 31.4264 14.9264V14.9264C32.1375 15.6375 32.7293 16.4585 33.179 17.3579L33.5316 18.0632C34.1684 19.3369 34.5 20.7414 34.5 22.1654V22.1654C34.5 23.3765 34.2602 24.5756 33.7944 25.6935L33.5785 26.2116C32.5603 28.6554 30.6971 30.6514 28.3292 31.8354V31.8354C26.7974 32.6013 25.1084 33 23.3959 33H19.5"
      stroke="white"
      stroke-width="4"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    iconColor?: string
  }>(),
  {
    iconColor: "#ffffff",
  },
)
</script>
