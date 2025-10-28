<template>
  <div v-if="isLoading" class="spinner-container">
    <div class="spinner"></div> <!-- Replace with a proper loading indicator -->
  </div>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  isLoading?: boolean
}>(), {
  isLoading: false
})
</script>