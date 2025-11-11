<template>
  <div
    class="text-white flex flex-col pt-0 md:pt-5 min-h-screen px-5"
    style="height: -webkit-fill-available"
  >
    <Header
      :subhead="true"
      :action="$attrs.action as string"
      :show-menu="true"
      :subhead-title="$attrs.title as string"
      @toggleSideMenu="toggleSideMenu"
    >
      <template #action>
        <slot name="action" />
      </template>
    </Header>
    <div class="flex flex-1 overflow-hidden">
      <SideMenu
        :is-data-loading="isLoading"
        :sideMenu="$attrs?.sideMenu || sideMenuTemplate"
        ref="sideMenuRef"
        class="lg:block lg:w-64 pl-0 md:pl-10"
      />
      <div class="flex-1 overflow-auto">
        <div
          v-if="$attrs.isChildLoading"
          class="flex items-center justify-center absolute z-[11] left-0 top-0 rounded-[10px] w-full h-full bg-black bg-opacity-70"
        >
          <div class="spinner"></div>
          <!-- Replace with a proper loading indicator -->
        </div>

        <slot />
      </div>
    </div>
    <Footer class="mt-auto" />
  </div>
</template>

<style scoped>
.spinner {
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-left-color: #ffffff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

<script setup lang="ts">
import { ref, watch, onMounted, useAttrs, reactive, type Component } from "vue"
import { Header, Footer } from "~/src/shared/ui/components"
import { SideMenu } from "~/src/widgets/navigation"
import { STUDIO_OWNER_ROLE, USER_ROLE } from "~/src/entities/Session"

const sideMenuRef = ref()
const isLoading = ref(false)
interface MenuItem {
  icon: Component
  name: string
  path: string
  link?: string
}

import {
  IconMic,
  IconBooking,
  IconUser,
  IconClients,
  IconHistory,
  IconClose,
  IconCredit,
  IconDollar,
  IconTeam,
  IconMonitor,
} from "~/src/shared/ui/common"

const sideMenuTemplate: MenuItem[] = [
  {
    name: "Profile",
    icon: IconUser,
    path: "/icons/profile.svg",
    link: "/profile",
    role: "",
  },
  {
    name: "Studios",
    icon: IconMic,
    path: "/icons/my-studios.svg",
    link: "/studios",
    role: USER_ROLE,
  },
  {
    name: "Team",
    icon: IconTeam,
    path: "/icons/my-studios.svg",
    link: "/team",
    role: STUDIO_OWNER_ROLE,
  },
  {
    name: "Booking management",
    icon: IconBooking,
    path: "/icons/profile.svg",
    link: "/bookings",
    role: "",
  },
  {
    name: "My Studios",
    icon: IconMic,
    path: "/icons/my-studios.svg",
    link: "/my-studios",
    role: STUDIO_OWNER_ROLE,
  },
  {
    name: "Clients",
    icon: IconClients,
    path: "/icons/settings.svg",
    link: "/clients",
    role: STUDIO_OWNER_ROLE,
  },
  {
    name: "History",
    icon: IconHistory,
    path: "/icons/settings.svg",
    link: "/history",
    role: STUDIO_OWNER_ROLE,
  },
  {
    name: "Payouts",
    icon: IconDollar,
    path: "/icons/dollar.svg",
    link: "/payout",
    role: STUDIO_OWNER_ROLE,
  },
  {
    name: "Devices",
    icon: IconMonitor,
    path: "/icons/monitor.svg",
    link: "/devices",
    role: STUDIO_OWNER_ROLE,
  },
  {
    name: "Chats",
    icon: IconHistory,
    path: "/icons/chat.svg",
    link: "/chats",
    role: "",
  },
]

interface MenuItem {
  icon: Component
  name: string
  path: string
  link?: string
  role?: string
}

const toggleSideMenu = () => {
  if (sideMenuRef.value) {
    sideMenuRef.value.toggleMenu()
  }
}
</script>
