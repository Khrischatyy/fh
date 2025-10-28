<template>
	<div class="flex justify-center">
		<div class="h-full w-full flex flex-col items-center">
      <script type="text/javascript" src="html-magnifier.js"></script>
			<app-header />

			<slot name="banner" />

			<main class="px-4 pb-6 w-full max-w-[1080px] min-[1080px]:px-0 mt-6 min-[1080px]:pb-9">
				<slot />
			</main>

			<app-footer v-if="props.showFooter" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { AppFooter, AppHeader } from 'widgets/Base'

const props = withDefaults(defineProps<{
	showFooter?: boolean
}>(), {
	showFooter: false
})
</script>

<style scoped>

</style>
