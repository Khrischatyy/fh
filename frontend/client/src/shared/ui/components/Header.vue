<template>
  <div class="w-full">
    <header
      class="mx-auto p-4 w-full md:max-w-7xl flex items-center relative justify-center"
    >
      <button
        v-if="showMenu"
        class="lg:hidden p-2 flex items-center absolute left-0"
        @click="$emit('toggleSideMenu')"
      >
        <IconBurger />
        <span class="hidden md:block ml-2 text-white">Menu</span>
      </button>
      <div
        @click="navigateTo('/')"
        class="flex hover:opacity-80 justify-center cursor-pointer"
      >
        <BrandingLogo :size="logoSize" />
      </div>
      <button
        v-if="!isAuth && !hideLoginButton"
        class="p-2 flex items-center gap-2 hover:opacity-70 absolute right-0"
        @click="navigateTo('/login')"
      >
        <div
          class="text-white hidden md:block text-2xl font-[BebasNeue]"
          style="
            line-height: 1.2em;
            padding-top: 4px;
            clip-path: inset(5px 0px 7px 0px);
          "
        >
          Sign In
        </div>
        <IconUser class="border-[1.5px] border-white rounded-full w-6 h-6" />
      </button>
      <button
        v-if="isAuth && !hideLoginButton"
        class="p-2 flex items-center gap-2 hover:opacity-70 absolute right-0"
        @click="navigateToProfile"
      >
        <div
          class="text-white hidden md:block text-2xl font-[BebasNeue]"
          style="
            line-height: 1.2em;
            padding-top: 4px;
            clip-path: inset(5px 0px 7px 0px);
          "
        >
          Profile
        </div>
        <div
          v-if="user && user.profile_photo"
          class="w-6 h-6 rounded-full border border-white"
        >
          <img
            class="object-cover rounded-full w-full"
            :src="user.profile_photo"
          />
        </div>
        <IconUser
          v-else
          class="border-[1.5px] border-white rounded-full w-6 h-6"
        />
      </button>
    </header>
    <div v-if="subhead" class="subhead flex flex-1 mb-4">
      <div class="subhead__back lg:w-64"></div>
      <div class="subhead__title px-2 md:px-4">
        <h1 class="text-3xl font-bold">{{ subheadTitle }}</h1>
      </div>
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, ref, computed } from "vue"
import { BrandingLogo } from "~/src/shared/ui/branding"
import { IconBurger, IconUser } from "~/src/shared/ui/common"
import { navigateTo } from "nuxt/app"
import { useCookie } from "#app"
import { ACCESS_TOKEN_KEY, useSessionStore } from "~/src/entities/Session"
import { storeToRefs } from "pinia"

const props = withDefaults(
  defineProps<{
    action?: string
    subhead?: boolean
    subheadTitle?: string
    hideLoginButton?: boolean
    showMenu?: boolean
    logoSize?: "default" | "small" | "large"
  }>(),
  {
    subhead: false,
    logoSize: "large",
  },
)
const sideMenuArray = ref([])

// Initialize session store on client-side only
let session: any = null
let user = ref(null)
if (process.client) {
  session = useSessionStore()
  const refs = storeToRefs(session)
  user = refs.user
}

const isAuth = useCookie(ACCESS_TOKEN_KEY).value
const emit = defineEmits(["toggleSideMenu"])
const navigateToProfile = () => {
  if (isAuth && session?.userRole === "studio_owner") {
    navigateTo("/my-studios")
  } else {
    navigateTo("/profile")
  }
}
</script>
