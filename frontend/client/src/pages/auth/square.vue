<script setup lang="ts">
import { useSessionStore } from "~/src/entities/Session"
import { useRouter } from "vue-router"
import { useHead } from "@unhead/vue"
import { useApi } from "~/src/lib/api"
import type { ResponseDto } from "~/src/lib/api/types"
import { Spinner } from "~/src/shared/ui/common"
import { Particles } from "~/src/shared/ui/components"
import { navigateTo } from "nuxt/app"
import { storeToRefs } from "pinia"
import { onMounted, ref } from "vue"
// Set the page metadata
useHead({
  title: "Funny How – Book a Session Time",
  meta: [{ name: "description", content: "Book A Studio Time | Auth" }],
})
const isLoading = ref(true)
const router = useRouter()
const error = ref("")
const route = router.currentRoute.value
const sessionStore = useSessionStore() // Retrieve session store
const { user } = storeToRefs(sessionStore)
const obtainToken = async (code: string) => {
  const setTokenApi = useApi({
    url: "/user/payment/square/callback",
    auth: true,
  })
  try {
    const response = await setTokenApi.post({ code })
    if (response?.data) {
      // Update the user's payment gateway directly, as the user is already logged in
      // Same happingin in the backend, but we need to update the user's payment gateway in the frontend without additional API calls
      sessionStore.setPaymentGateway("square")
      navigateTo("/payout")
    }
  } catch (err) {
    error.value = "Error obtain token: " + err?.errors?.errors?.[0]?.detail
  } finally {
    isLoading.value = false
  }
}
onMounted(() => {
  const code = route.query.code as string | undefined
  if (code) {
    obtainToken(code)
  } else {
    error.value = "No code found"
    isLoading.value = false
  }
})
</script>

<template>
  <div>
    <client-only>
      <div
        class="flex justify-center items-center text-white text-xxl h-full min-h-screen"
        style="height: -webkit-fill-available"
      >
        <Spinner :is-loading="isLoading" />
        <div class="error flex flex-col gap-10">
          <div v-if="error" class="text-center">
            <p class="text-2xl">{{ error }}</p>
          </div>
          <div class="flex flex-col gap-5">
            <div v-if="!error && !isLoading" class="text-center">
              <p class="text-xl">Successfully connected</p>
            </div>
            <div
              v-if="!isLoading"
              class="flex justify-center items-center gap-2.5"
            >
              <button
                @click="navigateTo('/payout')"
                class="max-w-96 h-11 p-3.5 px-10 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
              >
                Go To Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
      <Particles :position="{ x: 0, y: 0, z: 0 }" />
    </client-only>
  </div>
</template>

<style scoped lang="scss"></style>
