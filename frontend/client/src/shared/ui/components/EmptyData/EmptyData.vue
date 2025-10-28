<template>
	<div class="flex flex-col items-center">
		<slot name="image" />
		<p class="mt-5 text-[22px]/[26px] font-bold">
			{{ titleText }}
		</p>
		<p class="mt-4 text-center">
			{{ props.description }}
		</p>
	</div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
// import { useTranslation } from 'shared/lib/i18n'
import Localization from './localization.json'

const { t } = useTranslation(Localization)

const props = withDefaults(defineProps<{
    title?: string,
	description: string
}>(), {
    title: ''
})

const titleText = computed<string>(() => props.title || t('emptyDataTitle'))
</script>