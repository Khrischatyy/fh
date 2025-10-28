<script setup lang="ts">
import { Popup } from "~/src/shared/ui/components"
import { navigateTo } from "nuxt/app"
import { computed, inject, onMounted, onUnmounted, ref } from "vue"
import {
  IconBackDraw,
  IconDown,
  IconLike,
  IconMic,
} from "~/src/shared/ui/common"
import IconStar from "~/src/shared/ui/common/Icon/IconStar.vue"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import { useApi } from "~/src/lib/api"
import { Spinner } from "~/src/shared/ui/common/Spinner"
import type { AddressFull } from "~/src/entities/Studio/api"
import { useLogin } from "~/src/entities/User/api"
import { FInputClassic } from "~/src/shared/ui/common"
import GoogleSignInButton from "~/src/shared/ui/components/GoogleSignInButton.vue"
const { loginUser, errors, isLoading, formValues, isError } = useLogin()
const props = withDefaults(
  defineProps<{
    showPopup: boolean
  }>(),
  {
    showPopup: false,
  },
)

async function authForm() {
  isLoading.value = true
  try {
    await loginUser(formValues)
    // Navigate or handle success as needed
  } catch (error) {
    console.error("Error submitting studio form:", error)
  } finally {
    isLoading.value = false
  }
}
const address = inject("address") as AddressFull | undefined
const emit = defineEmits<{
  (e: "togglePopup"): void
  (e: "closePopup"): void
}>()

onMounted(() => {})

const closePopup = () => {
  emit("closePopup")
}
</script>

<template>
  <Popup
    :scroll-to-close="true"
    type="medium"
    :title="'Equipments'"
    :open="showPopup"
    @close="closePopup"
  >
    <template #header>
      <div class="flex justify-start items-center gap-5">
        <div>
          <div
            class="text-4xl font-bold cursor-pointer select-none font-['BebasNeue'] text-white"
          >
            Please Log In To Continue
          </div>
        </div>
      </div>
    </template>

    <template #action_header>
      <div class="text-white text-4xl text-right font-bold hover:opacity-70">
        <button @click="closePopup">
          <IconBackDraw />
        </button>
      </div>
    </template>
    <template #body>
      <div
        class="flex flex-col gap-7 max-w-96 w-full m-auto justify-center items-center relative"
      >
        <Spinner :is-loading="isLoading" />
        <div
          ref="auth"
          class="translate-x-[0px] duration-[700ms] relative w-full flex-col justify-start items-center gap-2.5 flex"
        >
          <FInputClassic
            size="lg"
            v-model="formValues.email"
            label="E-mail"
            type="email"
            :error="isError('email')"
          />
          <FInputClassic
            size="lg"
            v-model="formValues.password"
            label="Password"
            type="password"
            :error="isError('password')"
          />
          <div
            class="w-full h-7 rounded-lg justify-start items-center gap-2.5 inline-flex"
          >
            <label
              for="sign-in-for-a-month"
              class="checkbox-wrapper flex gap-2 cursor-pointer"
            >
              <div class="w-4 h-4 justify-center items-center flex">
                <input
                  id="sign-in-for-a-month"
                  type="checkbox"
                  class="hidden"
                />
                <div
                  class="w-4 h-4 rounded-[3px] border border-white custom-checkbox"
                ></div>
              </div>
              <div class="text-white text-sm font-normal tracking-wide">
                Stay signed in for a month
              </div>
            </label>
          </div>

          <div class="flex flex-col w-full items-center gap-2.5">
            <button
              @click="authForm()"
              class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
            >
              Sign In
            </button>

            <div class="justify-center w-full items-center gap-2.5 inline-flex">
              <button
                @click="navigateTo('/login')"
                class="w-full min-h-11 h-auto p-3.5 hover:opacity-90 rounded-[10px] text-white border text-sm font-medium tracking-wide"
              >
                Don’t have an account? Create account
              </button>
            </div>
            <GoogleSignInButton />
          </div>
          <div
            class="w-full h-11 p-3.5 justify-center items-center gap-2.5 inline-flex"
          >
            <button
              @click="navigateTo('/forgot-password')"
              class="w-full h-11 p-3.5 hover:opacity-90 rounded-[10px] text-white text-sm font-medium tracking-wide"
            >
              Forgot password?
            </button>
          </div>
        </div>
      </div>
    </template>
    <template #footer> </template>
  </Popup>
</template>

<style scoped lang="scss">
.custom_transition {
  transition: max-height 0.3s ease-in-out;
}
</style>
