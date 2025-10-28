<script setup lang="ts">
import {
  ChooseRole,
  CreateAccountForm,
} from "~/src/features/Register/createAccount"
import { provide, ref } from "vue"
import { useCreateAccount } from "~/src/entities/User/api"
const emit = defineEmits(["stepUpdate"])
const step = ref("create")

const { registerUser, errors, isLoading, formValues, isError } =
  useCreateAccount()

const handleRoleUpdate = (role: string) => {
  formValues.role = role
  step.value = "create_account"
}

const handleBackNavigation = () => {
  step.value = "auth" // Navigate back to the sign-in screen
}
const stepUpdate = ($event: string) => {
  emit("stepUpdate", $event)
}

provide("createForm", {
  formValues,
  errors,
  isLoading,
  isError,
  registerUser,
})
</script>

<template>
  <ChooseRole
    @updateRole="handleRoleUpdate"
    @navigate-back="stepUpdate"
    v-if="step == 'create'"
    ref="create"
    :class="
      step == 'create'
        ? 'translate-x-[0px] duration-[700ms]'
        : 'ml-96 translate-x-96 duration-700 opacity-0'
    "
    class="relative w-full flex-col justify-start items-center gap-2.5 flex"
  />

  <CreateAccountForm
    @step-update="stepUpdate"
    v-if="step == 'create_account'"
    ref="create_account"
    :class="
      step == 'create_account'
        ? 'translate-x-[0px] duration-[700ms]'
        : 'opacity-0 translate-x-96 duration-700'
    "
    class="relative w-full flex-col justify-start items-center gap-2.5 flex"
  />
</template>

<style scoped lang="scss"></style>
