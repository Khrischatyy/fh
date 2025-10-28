<template>
  <svg
    width="22"
    height="23"
    :opacity="active ? 1 : 0.2"
    viewBox="0 0 22 23"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g>
      <circle cx="11" cy="11.5" r="8.25" stroke="white" />
      <path
        d="M11.4582 7.37435C11.4582 7.62748 11.253 7.83268 10.9998 7.83268C10.7467 7.83268 10.5415 7.62748 10.5415 7.37435C10.5415 7.12122 10.7467 6.91602 10.9998 6.91602C11.253 6.91602 11.4582 7.12122 11.4582 7.37435Z"
        fill="white"
        stroke="white"
      />
      <path d="M11 16.0827V9.66602" stroke="white" />
    </g>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    active?: boolean
  }>(),
  {
    active: false,
  },
)
</script>
