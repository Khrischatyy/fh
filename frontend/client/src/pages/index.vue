<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { ref, onMounted, watch } from "vue"
import { ACCESS_TOKEN_KEY, useSessionStore } from "~/src/entities/Session"
import { useCookie } from "#app"
import GoogleSignInButton from "~/src/shared/ui/components/GoogleSignInButton.vue"
import PhoneSignInButton from "~/src/shared/ui/components/PhoneSignInButton.vue"
import PhoneAuthInput from "~/src/features/Auth/phone-login/ui/PhoneAuthInput.vue"
import { Header, Footer } from "~/src/shared/ui/components"

useHead({
  title: "Funny How – Book a Session Time",
  meta: [{ name: "Funny How", content: "Book A Studio Time" }],
})

const isBrand = ref("")
const session = useSessionStore()
const showPhoneAuth = ref(false)

watch(
  () => session.brand,
  (newValue) => {
    isBrand.value = <string>newValue
  },
)

onMounted(() => {
  isBrand.value = <string>session.brand
})

function signOut() {
  useSessionStore().logout()
}

function handlePhoneAuthSuccess() {
  showPhoneAuth.value = false
  // User is now authenticated via session store
}

function handlePhoneAuthCancel() {
  showPhoneAuth.value = false
}
</script>

<template>
  <div
    class="ease-in-out min-h-screen px-5 w-full flex flex-col gap-10 pt-0 md:pt-5 items-center justify-between bg-black"
    style="height: -webkit-fill-available"
  >
    <Header />
    <div
      class="h-full min-h-[50vh] w-full flex-1 justify-center items-center flex flex-col gap-2"
    >
      <div class="font-[BebasNeue] flex flex-col text-center gap-5">
        <RouterLink
          to="/map"
          class="text-4xl text-white uppercase hover:opacity-70"
        >
          <div class="flex gap-3 justify-center items-center">
            <div class="font-['BebasNeue']">Find Some Here</div>
            <img
              class="h-[30px]"
              src="../shared/assets/image/map.svg"
              alt="Funny How"
            />
          </div>
        </RouterLink>
        <RouterLink
          to="/studios"
          class="text-4xl text-white uppercase hover:opacity-70 flex justify-center"
        >
          <div class="font-['BebasNeue']">Lock In Your Session</div>
          <div
            class="flex items-center justify-center relative -translate-y-1 translate-x-2"
          >
            <img
              class="h-[25px]"
              src="../shared/assets/image/lockin.svg"
              alt="Funny How"
            />
          </div>
        </RouterLink>
      </div>

      <!-- Auth Buttons (shown when not authenticated) -->
      <div v-if="!useCookie(ACCESS_TOKEN_KEY).value" class="flex flex-col items-center gap-3 mt-10">
        <GoogleSignInButton />

        <!-- Phone Sign In Button (toggles inline form) -->
        <PhoneSignInButton
          v-if="!showPhoneAuth"
          @click="showPhoneAuth = true"
        />

        <!-- Inline Phone Auth Form -->
        <PhoneAuthInput
          v-if="showPhoneAuth"
          @success="handlePhoneAuthSuccess"
          @cancel="handlePhoneAuthCancel"
          class="mt-4"
        />
      </div>

      <div
        v-if="useCookie(ACCESS_TOKEN_KEY).value"
        class="justify-center w-full max-w-96 p-5 items-center gap-2.5 inline-flex mt-10"
      ></div>
    </div>
    <Footer />
  </div>
</template>

<style scoped lang="scss">
.font-bebas {
  font-family: "BebasNeue", sans-serif;
}
</style>
