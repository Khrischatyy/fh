<script setup lang="ts">
import { ChooseRole } from "~/src/features/Register/createAccount"
import { useHead } from "@unhead/vue"
import { definePageMeta } from "#imports"
import { inject, onMounted, reactive, ref } from "vue"
import { useApi } from "~/src/lib/api"
import { useSessionStore } from "~/src/entities/Session"
import { Particles } from "~/src/shared/ui/components"
import { IconElipse, IconLine } from "~/src/shared/ui/common"
import BrandingLogo from "../../shared/ui/branding/BrandingLogo.vue"
import { navigateTo } from "nuxt/app"

useHead({
  title: "Funny How – Book a Session Time",
  meta: [{ name: "Funny How", content: "Book A Studio Time" }],
})

definePageMeta({
  middleware: "auth",
})

const roleValue = ref("")
const { post } = useApi({
  url: "/user/set-role",
  auth: true,
})
const session = useSessionStore()
const isLoading = ref(true)

onMounted(() => {
  roleValue.value = session.userRole as string
  isLoading.value = false

  if (roleValue.value === "studio_owner") {
    navigateTo("/create")
  } else if (roleValue.value === "user") {
    navigateTo("/studios")
  }
})
const handleBackNavigation = () => {
  window.history.back()
}
const handleRoleUpdate = async (role: string) => {
  roleValue.value = role
  await post({ role: role })
    .then((response) => {
      session.setUserRole(response?.data)
      if (role === "studio_owner") {
        navigateTo("/create")
      } else {
        navigateTo("/studios")
      }
    })
    .catch((error) => {
      console.error("error", error)
    })
}
</script>

<template>
  <div
    class="duration-[700ms] ease-in-out grid min-h-screen h-full animate__animated animate__fadeInRight"
    style="height: -webkit-fill-available"
  >
    <div class="auth-panel bg-[#000000] relative">
      <div
        class="w-full h-full flex sm:grid items-start lg:items-center justify-center mb-10"
      >
        <div
          class="relative flex-col justify-start w-full items-center gap-7 inline-flex"
        >
          <BrandingLogo class="lg:hidden mb-10 mt-10" />
          <div
            :class="'-translate-x-96/2 duration-700'"
            class="breadcrumbs hidden sm:flex text-white text-sm font-normal tracking-wide gap-1.5 justify-center items-center"
          >
            <icon-elipse :class="'opacity-100'" class="h-4" />
            <button :class="'opacity-100'">Your Role</button>
            <icon-line :class="'opacity-100'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <button :class="'opacity-20'">Personal Info</button>
            <icon-line :class="'opacity-20'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <button :class="'opacity-20'">Price Plans</button>
            <icon-line :class="'opacity-20'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <button :class="'opacity-20'">Add Studio</button>
          </div>
          <div
            class="relative h-full hidden sm:block text-white text-3xl font-bold tracking-wider"
          >
            Choose Role
          </div>
          <div
            class="relative h-full w-full sm:w-auto m-2 md:m-0 md:w-96 min-h-auto sm:min-h-[500px] flex justify-start items-center bg-gradient-to-b from-[#000] via-[#000] to-transparent rounded-xl p-5 z-10"
          >
            <ChooseRole
              :selected-role="roleValue"
              @updateRole="handleRoleUpdate"
              @navigateBack="handleBackNavigation"
              ref="create"
              class="translate-x-[0px] duration-[700ms] relative w-full flex-col justify-start items-center gap-2.5 flex max-w-96"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.checkbox-wrapper {
  display: flex;
  gap: 5px;
  cursor: pointer;

  .custom-checkbox {
    display: inline-block;
    vertical-align: middle;
    position: relative;

    &:after {
      content: "";
      position: absolute;
      display: none;
    }
  }

  input[type="checkbox"] {
    &:checked ~ .custom-checkbox {
      padding: 3px;
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;

      &:after {
        position: relative;
        top: 0;
        left: 0;
        display: block;
        width: 100%;
        height: 100%;
        border: solid white;
        background: #f3f5fd;
        border-radius: 2px;
      }
    }
  }
}
</style>
