<template>
	<div class="v-card">
		<template
			v-if="slots.header"
		>
			<slot
				name="header"
			/>
		</template>
		<div
			v-else-if="props.title"
			class="flex items-center gap-4"
		>
			<template
				v-if="slots.image"
			>
				<slot name="image" />
			</template>
			<div
				class="flex flex-col gap-1"
			>
				<p class="text-[22px]/[26px] font-bold">
					{{ props.title }}
				</p>
				<p
					v-if="subtitle"
					class="text-gray-100"
				>
					{{ props.subtitle }}
				</p>
			</div>
		</div>
		<slot />
	</div>
</template>

<script setup lang="ts">
import { useSlots } from 'vue'

const props = withDefaults(defineProps<{
    title?: string,
    subtitle?: string
}>(), {
    title: '',
    subtitle: ''
})

const slots = useSlots()
</script>

<style scoped lang="scss">
.v-card {
    @apply flex flex-col p-4 bg-white rounded-[20px] md:p-6;
    box-shadow: 0px 4px 40px 0px rgba(0, 0, 0, 0.10);
}
</style>