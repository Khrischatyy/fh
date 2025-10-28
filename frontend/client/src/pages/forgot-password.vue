<template>
  <div class="w-full px-5">
    <Spinner :is-loading="isLoading" />
    <div class="flex flex-col gap-10 justify-center items-center">
      <div class="text-center flex flex-col gap-5">
        <h1 class="text-4xl font-bold">Forgot Password</h1>
        <p class="text-xl">Enter your email to reset your password</p>
      </div>

      <div
        class="flex flex-col gap-2.5 max-w-96 w-full justify-center items-center"
      >
        <FInputClassic
          :error="isError('email')"
          :success="success"
          type="email"
          class="w-full"
          v-model="email"
          placeholder="youremail@example.com"
          required
        />
        <button
          @click="forgotPassword()"
          class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide mt-4"
        >
          Send Reset Link
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
import { ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import { FInputClassic } from "../shared/ui/common"
import { navigateTo } from "#app"
import { Spinner } from "../shared/ui/common"
import { IconLeft } from "../shared/ui/common"
import { definePageMeta } from "#imports"
import { useApi } from "../lib/api"
const email = ref("")
const router = useRouter()
const isLoading = ref(false)
// Meta tags for the page
definePageMeta({
  layout: "error",
})

const errors = ref<string[]>([])
const success = ref<string>("")
function isError(field): string | boolean {
  if (errors.value?.hasOwnProperty(field)) {
    const errorMessages = errors.value[field]
    if (errorMessages && errorMessages.length > 0) {
      return errorMessages[0] // Return the first error message
    }
  }
  return false // Return false if no errors are found
}

const forgotPassword = async () => {
  isLoading.value = true
  const { post } = useApi({
    url: "auth/forgot-password",
  })
  errors.value = []
  success.value = ""
  await post({
    email: email.value,
  })
    .then((response) => {
      isLoading.value = false
      email.value = ""
      success.value = "Password reset link sent! Check your email."
      setInterval(() => {
        success.value += "."
      }, 1000)
      setTimeout(() => {
        router.push("/login")
      }, 4000)
    })
    .catch((error) => {
      isLoading.value = false
      errors.value = error.errors
    })
}
</script>

<style scoped lang="scss"></style>
