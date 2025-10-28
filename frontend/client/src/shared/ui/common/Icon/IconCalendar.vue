<template>
  <svg
    width="42"
    height="42"
    viewBox="0 0 42 42"
    :opacity="active ? 1 : 0.2"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g>
      <path
        d="M5.25 18.1364C5.25 14.5365 5.25 12.7366 6.36832 11.6183C7.48664 10.5 9.28655 10.5 12.8864 10.5H29.1136C32.7135 10.5 34.5134 10.5 35.6317 11.6183C36.75 12.7366 36.75 14.5365 36.75 18.1364V19.25H5.25V18.1364Z"
        stroke="white"
      />
      <rect
        x="5.25"
        y="10.5"
        width="31.5"
        height="26.25"
        rx="3.81818"
        stroke="white"
      />
      <path
        d="M14.0005 5.25L14.0005 12.25"
        stroke="white"
        stroke-linecap="round"
      />
      <path
        d="M27.9995 5.25L27.9995 12.25"
        stroke="white"
        stroke-linecap="round"
      />
    </g>
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
