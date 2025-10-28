<template>
  <svg
    width="42"
    height="42"
    viewBox="0 0 42 42"
    fill="none"
    :opacity="active ? 1 : 0.2"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="20.9995" cy="21.001" r="14.5" stroke="white" />
    <path
      d="M28.875 21.001H21.4773C21.2137 21.001 21 20.7873 21 20.5237V14.876"
      stroke="white"
      stroke-linecap="round"
    />
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    iconColor?: string
    active?: boolean
  }>(),
  {
    iconColor: "#ffffff",
    active: false,
  },
)
</script>
