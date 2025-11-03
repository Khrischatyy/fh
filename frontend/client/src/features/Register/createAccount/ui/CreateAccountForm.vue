<template>
  <div>
    <div
      v-if="isError('general')"
      class="w-96 justify-center items-center inline-flex"
    >
      <div class="text-red-500 text-sm font-normal tracking-wide">
        {{ isError("general") }}
      </div>
    </div>
    <FInputClassic
      size="lg"
      v-model="formValues.name"
      label="Name"
      type="text"
      autocomplete="name"
      :error="isError('name')"
    />
    <FInputClassic
      size="lg"
      v-model="formValues.email"
      label="E-mail"
      type="email"
      autocomplete="email"
      :error="isError('email')"
    />
    <FInputClassic
      size="lg"
      v-model="formValues.password"
      label="Password"
      type="password"
      autocomplete="new-password"
      :error="isError('password')"
    />
    <FInputClassic
      size="lg"
      v-model="formValues.password_confirmation"
      label="Confirm Password"
      type="password"
      autocomplete="new-password"
      :error="isError('password_confirmation')"
    />
    <div class="justify-center items-center gap-2.5 inline-flex w-full">
      <button
        @click="createAccount()"
        :disabled="isLoading"
        class="max-w-96 w-full h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
      >
        Submit {{ isLoading ? "loading..." : "" }}
      </button>
    </div>
    <div
      class="max-w-96 w-full h-11 p-3.5 justify-between items-center gap-2.5 inline-flex"
    >
      <button
        @click="$emit('stepUpdate', 'auth')"
        class="w-full flex justify-center h-11 p-3.5 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
      >
        <icon-left />
        Back to Sign In
      </button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { FInputClassic } from "~/src/shared/ui/common"
import { inject, ref } from "vue"
import { IconLeft } from "~/src/shared/ui/common"
type CreateForm = {
  formValues: {
    name: string
    email: string
    password: string
    password_confirmation: string
    role: string
  }
  errors: {
    [key: string]: string | undefined
  }
  isLoading: boolean
  isError: (field: string) => string | undefined
  registerUser: () => Promise<void>
}

const createForm = inject<CreateForm>("createForm")
if (!createForm) {
  throw new Error("createForm is not provided")
}

const { formValues, errors, isLoading, isError, registerUser } =
  inject("createForm")

// const store = useCreateAccountFormStore();
const emit = defineEmits(["stepUpdate"])
const createAccount = async () => {
  isLoading.value = true
  try {
    await registerUser(formValues)
    // Navigate or handle success as needed
  } catch (error) {
    console.error("Error submitting user form:", error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style lang="scss" scoped></style>
