<template>
  <div class="flex items-center justify-center min-h-screen bg-black">
    <div class="text-white text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
      <p class="text-lg">Connecting you to support...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from '#app'
import { useRuntimeConfig } from '#imports'
import { useSessionStore } from '~/src/entities/Session'
import { useApi } from '~/src/lib/api'

const router = useRouter()
const config = useRuntimeConfig()
const session = useSessionStore()

const SUPPORT_USER_ID = Number(config.public.supportUserId) || 1
const SUPPORT_ADDRESS_ID = Number(config.public.supportAddressId) || 1

onMounted(async () => {
  // Redirect to login if not authorized
  if (!session.isAuthorized) {
    router.replace('/login?redirect=/support')
    return
  }

  try {
    // Fetch all user's chats
    const { fetch } = useApi({ url: '/messages/chats', auth: true })
    const response = await fetch() as { data: any[] }

    // Find existing support chat
    const supportChat = response.data.find(
      (chat: any) => chat.customer_id === SUPPORT_USER_ID
    )

    if (supportChat) {
      // Support chat exists, redirect to it
      console.log('[support] Found existing support chat:', supportChat.id)
      router.replace(`/chats/${supportChat.id}`)
    } else {
      // No support chat yet, redirect to new chat page
      console.log('[support] No existing support chat, creating new one')
      router.replace(`/chats/new?recipient_id=${SUPPORT_USER_ID}&address_id=${SUPPORT_ADDRESS_ID}`)
    }
  } catch (err) {
    console.error('[support] Error loading support chat:', err)
    // Fallback: go to new chat page
    router.replace(`/chats/new?recipient_id=${SUPPORT_USER_ID}&address_id=${SUPPORT_ADDRESS_ID}`)
  }
})
</script>
