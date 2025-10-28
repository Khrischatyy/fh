<template>
	<v-input
		:label="t('passwordFieldLabel')"
		:placeholder="t('passwordFieldLabel')"
		:show-password="!isVisible"
		:model-value="password"
		data-test="input_of_password"
		@input="onInput"
	>
		<template #suffix>
			<div
				class="cursor-pointer text-gray-100 hover:text-purple"
				@click="toggleVisibility"
			>
				<icon-eye-closed v-show="!isVisible" />
				<icon-eye v-show="isVisible" />
			</div>
		</template>
	</v-input>
</template>

<script setup lang="ts">
import { IconEye, IconEyeClosed, VInput } from 'shared/ui/common'
import { ref, watchEffect } from 'vue'
import Localization from './PasswordField.localization.json'
// import { useTranslation } from 'shared/lib/i18n'

const { t } = useTranslation(Localization)

const isVisible = ref<boolean>(false)

const emit = defineEmits<{
	(event: 'update:modelValue', password: string): void
}>()

const props = defineProps<{
	modelValue: string
}>()

const password = ref<string>(props.modelValue)
watchEffect(() => {
	password.value = props.modelValue
})

const toggleVisibility = () => {
	isVisible.value = !isVisible.value
}

const onInput = (value: string) => {
	emit('update:modelValue', value)
}
</script>

<style lang="scss" scoped>
:deep(.el-input) {
	.el-icon {
		display: none;
	}
}
</style>
