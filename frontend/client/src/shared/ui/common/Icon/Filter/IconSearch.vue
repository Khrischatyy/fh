<template>
  <svg
    width="22"
    height="23"
    viewBox="0 0 22 23"
    :opacity="active ? 1 : 0.2"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="10.0832" cy="10.5827" r="6.41667" stroke="white" />
    <path
      d="M18.3335 18.834L15.5835 16.084"
      stroke="white"
      stroke-linecap="round"
    />
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
