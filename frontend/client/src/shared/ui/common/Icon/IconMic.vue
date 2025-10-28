<template>
  <svg width="23" height="29" viewBox="0 0 23 29" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M11.4997 19.0215C14.3543 19.0215 16.6663 16.7094 16.6663 13.8548V6.75065C16.6663 3.89607 14.3543 1.58398 11.4997 1.58398C8.64509 1.58398 6.33301 3.89607 6.33301 6.75065V13.8548C6.33301 16.7094 8.64509 19.0215 11.4997 19.0215Z" :stroke="iconColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M1.61914 11.4652V13.661C1.61914 19.1118 6.04956 23.5423 11.5004 23.5423C16.9512 23.5423 21.3816 19.1118 21.3816 13.661V11.4652M9.70497 7.30602C10.8675 6.87977 12.1333 6.87977 13.2958 7.30602M10.4671 10.0443C11.1516 9.86352 11.8621 9.86352 12.5466 10.0443M11.5004 23.5423V27.4173" :stroke="iconColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</template>
<script setup lang="ts">
const props = withDefaults(defineProps<{
  iconColor?: string,
}>(), {
  iconColor: '#ffffff',
})
</script>