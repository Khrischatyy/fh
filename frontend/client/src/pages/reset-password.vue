<template>
  <div class="w-full px-5">
    <Spinner :is-loading="isLoading" />
    <div class="flex flex-col gap-10 justify-center items-center">
      <div class="text-center flex flex-col gap-5">
        <h1 class="text-4xl font-bold">Reset Password</h1>
        <p class="text-xl">Enter your new password</p>
      </div>

      <div
        class="flex flex-col gap-2.5 max-w-96 w-full justify-center items-center"
      >
        <FInputClassic
          :error="isError('password')"
          :success="success"
          class="w-full"
          :disabled="success.length > 0"
          type="password"
          v-model="password"
          placeholder="New Password"
          required
        />
        <FInputClassic
          class="w-full"
          type="password"
          :disabled="success.length > 0"
          v-model="password_confirmation"
          placeholder="Confirm New Password"
          required
        />
        <button
          @click="resetPassword()"
          :disabled="success.length > 0"
          class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
        >
          Reset Password
        </button>
      </div>

      <div
        class="max-w-96 w-full h-11 p-3.5 justify-between items-center gap-2.5 inline-flex"
      >
        <button
          @click="navigateTo('/login')"
          class="w-full flex justify-center h-11 p-3.5 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
        >
          <icon-left />
          Back to Sign In
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import axios from "axios"
import { FInputClassic } from "../shared/ui/common"
import { navigateTo } from "#app"
import { Spinner } from "../shared/ui/common"
import { IconLeft } from "../shared/ui/common"
import { definePageMeta } from "#imports"
import { useApi } from "../lib/api"
import { useSessionStore } from "../entities/Session"
const router = useRouter()
const isLoading = ref(false)
// Meta tags for the page
definePageMeta({
  layout: "error",
})

const errors = ref<any>([])
const success = ref<string>("")
const route = useRoute()
const password = ref("")
const password_confirmation = ref("")

const token = computed(() => route.query.token)
const email = computed(() => route.query.email)

function isError(field): string | boolean {
  if (errors.value?.errors?.hasOwnProperty(field)) {
    const errorMessages = errors.value?.errors[field]
    if (errorMessages && errorMessages.length > 0) {
      return errorMessages[0] // Return the first error message
    }
  } else {
    return errors.value.message // Return the first error message
  }
  return false // Return false if no errors are found
}
const sessionStore = useSessionStore()
const resetPassword = async () => {
  isLoading.value = true

  if (!token.value || !email.value) {
    errors.value = { message: "Invalid token or email" }
    isLoading.value = false
    return
  }

  const { post } = useApi({
    url: "auth/reset-password",
  })
  errors.value = []
  success.value = ""
  await post({
    token: token.value,
    email: email.value,
    password: password.value,
    password_confirmation: password_confirmation.value,
  })
    .then((response) => {
      isLoading.value = false
      email.value = ""
      success.value = "Password updated successfully! Redirecting"

      sessionStore.authorize(response?.data.token)

      setInterval(() => {
        success.value += "."
      }, 1000)
      setTimeout(() => {
        router.push("/profile")
      }, 2000)
    })
    .catch((error) => {
      isLoading.value = false
      console.error("errrors", error)
      errors.value = error
    })
}
</script>

<style scoped lang="scss"></style>
