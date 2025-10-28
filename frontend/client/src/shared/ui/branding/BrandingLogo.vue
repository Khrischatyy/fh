<template>
  <img
      :class="{
      'h-[60px] md:h-[70px]': props.size === 'default',
      'h-[40px] md:h-[50px]': props.size === 'small',
      'h-[80px] md:h-[90px]': props.size === 'large',
      'h-[100px] md:h-[150px]': props.size === 'superLarge',
    }"
      src="./assets/funny-how-logo.svg"
      alt="Funny How"
  />
</template>
<script setup lang="ts">
const props = withDefaults(
    defineProps<{
      size?: "default" | "small" | "large" | "superLarge";
    }>(),
    {
      size: "large",
    },
)
</script>
