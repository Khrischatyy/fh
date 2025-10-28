<template>
  <svg
    width="43"
    height="43"
    viewBox="0 0 43 43"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect
      width="43"
      height="43"
      rx="10"
      :fill="isActive ? 'transparent' : '#ffffff'"
      stroke="#ffffff"
      :stroke-width="2"
      stroke-opacity="0.2"
    />
    <path
      d="M21.5 16.5L29.5 16.5"
      :stroke="isActive ? '#ffffff' : '#171717'"
      stroke-width="2"
      stroke-linecap="round"
    />
    <path
      d="M13.5 16.5L17.5 16.5"
      :stroke="isActive ? '#ffffff' : '#171717'"
      stroke-width="2"
      stroke-linecap="round"
    />
    <path
      d="M26.5 26.5L29.5 26.5"
      :stroke="isActive ? '#ffffff' : '#171717'"
      stroke-width="2"
      stroke-linecap="round"
    />
    <path
      d="M13.5 26.5L21.5 26.5"
      :stroke="isActive ? '#ffffff' : '#171717'"
      stroke-width="2"
      stroke-linecap="round"
    />
    <circle
      cx="19.5"
      cy="16.5"
      r="2"
      transform="rotate(90 19.5 16.5)"
      :stroke="isActive ? '#ffffff' : '#171717'"
      stroke-width="2"
      stroke-linecap="round"
    />
    <circle
      cx="24.5"
      cy="26.5"
      r="2"
      transform="rotate(90 24.5 26.5)"
      :stroke="isActive ? '#ffffff' : '#171717'"
      stroke-width="2"
      stroke-linecap="round"
    />
  </svg>
</template>
<script setup lang="ts">
const props = defineProps<{
  isActive?: boolean | string
}>()
</script>
