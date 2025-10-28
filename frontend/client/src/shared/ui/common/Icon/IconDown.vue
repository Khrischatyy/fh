<template>
  <svg
    :style="{
      transform: `rotate(${rotation}deg)`,
      transition: '0.3s cubic-bezier(0.25, 1, 0.5, 1)',
    }"
    width="25"
    height="25"
    viewBox="0 0 25 25"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g :opacity="opacity">
      <path
        d="M12.3079 15.2695L8.59346 10.8121C8.15924 10.2911 8.52976 9.5 9.20803 9.5H15.792C16.4702 9.5 16.8408 10.2911 16.4065 10.8121L12.6921 15.2695C12.5921 15.3895 12.4079 15.3895 12.3079 15.2695Z"
        fill="white"
      />
    </g>
  </svg>
</template>

<script setup lang="ts">
const props = defineProps({
  opacity: {
    type: Number,
    default: 1,
  },
  rotation: {
    type: Number,
    default: 0,
  },
})
</script>
