<template>
	<v-dialog
		v-model="isDialogVisible"
		show-close
		@close="onDialogClose"
	>
		<template #header>
			<div class="flex justify-center">
				<branding-logo />
			</div>
		</template>

		<div class="flex flex-col gap-4 mb-10">
			<v-input
				v-model="model.login"
				data-test="input_of_login"
				:label="t('login_field_label')"
				:placeholder="t('login_field_placeholder')"
			/>

			<password-field
				v-model="model.password"
			/>

			<v-checkbox
				v-model="model.rememberMe"
			>
				{{ t('remember_me_button_text') }}
			</v-checkbox>
		</div>

		<div
			v-loading="isLoading"
			class="flex flex-row md:items-start gap-2 items-center justify-center mb-6 buttons-container"
		>
			<v-button
				data-test="button_of_register"
				:size="ButtonSizeEnum.Large"
				outline
			>
				{{ t('register_button_text') }}
			</v-button>

			<v-button
				data-test="button_of_log-in"
				:disabled="isLoading"
				:size="ButtonSizeEnum.Large"
				@click="login"
			>
				{{ t('log_in_button_text') }}
			</v-button>
		</div>

		<div class="flex flex-col-reverse gap-2 items-center justify-center md:flex-row md:items-start buttons-container">
			<span class="cursor-pointer text-purple text-base font-bold"> {{ t('forgot_password_button_text') }} </span>
		</div>
	</v-dialog>
</template>

<script setup lang="ts">
import { VDialog, VInput, VCheckbox, VButton, ButtonSizeEnum } from 'shared/ui/common'
import { BrandingLogo } from 'shared/ui/branding'
import { ref } from 'vue'
import PasswordField from './PasswordField.vue'
// import { useTranslation } from 'shared/lib/i18n'
import { useAuthorization } from '../model'
import Localization from './LogInFlow.localization.json'
import { navigateTo } from 'nuxt/app'

const { t } = useTranslation(Localization)

const {
  model,
  isLoading,
  authorize,
  resetData
} = useAuthorization()

const isDialogVisible = ref<boolean>(false)

const start = () => {
	isDialogVisible.value = true
}

const login = async () => {
	const { data } = await authorize()

	if (data?.success) {
		isDialogVisible.value = false
		navigateTo('/home')
	}
}

const onDialogClose = () => {
  resetData()
}

defineExpose({
	start
})

</script>

<style lang="scss" scoped>
.buttons-container {
  @apply flex flex-col-reverse md:flex-row;

	:deep(.el-button) {
		@apply text-base min-w-[180px] w-full md:w-auto;
	}
}
</style>
