<template>
  <div class="w-full px-5">
    <Spinner :is-loading="isLoading" />
    <div class="flex flex-col gap-10 justify-center items-center">
      <div class="text-center flex flex-col gap-5">
        <h1 class="text-4xl font-bold">Error occured</h1>
        <p class="text-xl">Creating new Stripe session</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { Spinner } from "~/src/shared/ui/common"
import { definePageMeta, storeToRefs } from "#imports"
import { useSessionStore } from "~/src/entities/Session"
import { useApi } from "~/src/lib/api"
const isLoading = ref(true)
// Meta tags for the page
definePageMeta({
  layout: "error",
})

const session = useSessionStore()
const { user } = storeToRefs(session)

const createAccountLink = async () => {
  try {
    isLoading.value = true
    const { fetch: getLink } = useApi({
      url:
        "/user/stripe/account/link?account_id=" + user.value.stripe_account_id,
      auth: true,
    })

    await getLink().then((res) => {
      if (res.data.url) {
        window.location.href = res.data.url
      }
    })
  } catch (error) {
    console.error("Failed to create account link:", error)
    isLoading.value = false
  }
}

onMounted(() => {
  createAccountLink()
})
</script>

<style scoped lang="scss"></style>
