<script setup lang="ts">
import { useSessionStore } from "~/src/entities/Session"
import { useRouter } from "vue-router"
import { useHead } from "@unhead/vue"
import { useApi } from "~/src/lib/api"
import type { ResponseDto } from "~/src/lib/api/types"
import { Particles } from "~/src/shared/ui/components"
import { navigateTo } from "nuxt/app"
// Set the page metadata
useHead({
  title: "Funny How – Book a Session Time",
  meta: [{ name: "description", content: "Book A Studio Time | Auth" }],
})

const router = useRouter()
const route = router.currentRoute.value
const sessionStore = useSessionStore() // Retrieve session store

// Directly handle the token from URL
const token = route.query.token as string | undefined
if (token) {
  sessionStore.authorize(token)
} else {
  router.push("/login")
}
</script>

<template>
  <div>
    <client-only>
      <Particles :position="{ x: 0, y: 0, z: 0 }" />
    </client-only>
  </div>
</template>

<style scoped lang="scss"></style>
