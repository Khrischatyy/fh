<template>
  <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="21.7083" cy="12.8333" r="3.83333" stroke="white" stroke-linecap="round"/>
    <path d="M15.2805 23.8702C15.9028 21.0676 18.6884 19.541 21.5592 19.541H21.8574C24.7283 19.541 27.5139 21.0676 28.1361 23.8702C28.2354 24.3175 28.3148 24.7809 28.3635 25.2511C28.4203 25.8004 27.969 26.2493 27.4167 26.2493H16C15.4477 26.2493 14.9964 25.8004 15.0532 25.2511C15.1018 24.7809 15.1812 24.3175 15.2805 23.8702Z" stroke="white" stroke-linecap="round"/>
    <circle cx="10" cy="8.75" r="5" fill="white" stroke="white" stroke-linecap="round"/>
    <path d="M1.97351 21.7796C2.7979 19.0297 5.52173 17.5 8.39258 17.5H11.6074C14.4783 17.5 17.2021 19.0297 18.0265 21.7796C18.3465 22.8471 18.6102 24.036 18.7086 25.251C18.7532 25.8014 18.3023 26.25 17.75 26.25H2.25C1.69772 26.25 1.24682 25.8014 1.2914 25.251C1.38979 24.036 1.65348 22.8471 1.97351 21.7796Z" fill="white" stroke="white" stroke-linecap="round"/>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(defineProps<{
  iconColor?: string,
}>(), {
  iconColor: '#ffffff',
})
</script>