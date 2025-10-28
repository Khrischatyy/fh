<template>
  <div class="w-full px-5">
    <Spinner :is-loading="isLoading" />
    <div class="flex flex-col gap-10 justify-center items-center">
      <div class="text-center flex flex-col gap-5">
        <h1 class="text-4xl font-bold">Account Setup Complete</h1>
        <p class="text-xl">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { Spinner } from "~/src/shared/ui/common"
import { definePageMeta } from "#imports"
import { useSessionStore } from "~/src/entities/Session"
import { navigateTo } from "#app"
import { useApi } from "~/src/lib/api"

const isLoading = ref(true)
const message = ref("Verifying account...")
const session = useSessionStore()

// Meta tags for the page
definePageMeta({
  layout: "error",
})

onMounted(async () => {
  try {
    message.value = "Updating account information..."
    
    // First, get fresh user data
    const { fetch: getMe } = useApi({
      url: "/user/me",
      auth: true,
    })
    
    const response = await getMe()
    console.log('User data:', response?.data) // Debug log
    
    if (response?.data?.user) {
      const userData = response.data.user
      
      // Check if Stripe account is properly connected
      if (!userData.stripe_account_id || !userData.payment_gateway) {
        throw new Error("Stripe account not properly connected")
      }
      
      // Update session store with fresh data
      session.userObject = response.data
      session.setUserInfo(JSON.stringify(response.data))
      session.setBrand(response.data.company_slug)
      session.setUserRole(response.data.role)
      session.setAuthorized(true)
      
      message.value = "Account setup complete. Redirecting..."
      setTimeout(() => {
        navigateTo("/payout")
      }, 2000)
    } else {
      throw new Error("Failed to get user data")
    }
  } catch (error) {
    console.error("Error updating account:", error)
    message.value = "Error updating account. Please try again."
    // Add retry button
    const retryBtn = document.createElement('button')
    retryBtn.textContent = 'Retry'
    retryBtn.className = 'mt-4 px-6 py-2 bg-white text-black rounded hover:bg-gray-200'
    retryBtn.onclick = () => window.location.reload()
    document.querySelector('.text-center')?.appendChild(retryBtn)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped lang="scss"></style>
