<template>
  <div class="container mx-auto px-2 md:px-4 flex flex-col" style="height: calc(100vh - 100px);">
      <!-- Chat header -->
      <div class="bg-[#171717] rounded-t-lg p-4 border-b border-white border-opacity-10">
        <h2 class="text-white text-lg font-semibold">{{ recipientName }}</h2>
        <p class="text-white/50 text-sm">Start a new conversation</p>
      </div>

      <!-- Empty messages state -->
      <div class="flex-1 overflow-y-auto bg-[#171717] p-4 flex items-center justify-center">
        <div class="text-center text-gray-400">
          <div class="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
          </div>
          <p class="text-lg mb-2">👋 Start the conversation</p>
          <p class="text-sm">Send your first message below</p>
        </div>
      </div>

      <!-- Message input -->
      <div class="bg-[#171717] rounded-b-lg p-4 border-t border-white border-opacity-10">
        <div v-if="isSending" class="mb-3 p-2 bg-blue-500/10 border border-blue-500/30 rounded text-blue-200 text-xs text-center">
          Sending message...
        </div>
        <div v-if="error" class="mb-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-red-200 text-xs text-center">
          {{ error }}
        </div>
        <div class="flex gap-2">
          <input
            v-model="newMessage"
            @keyup.enter="handleSendMessage"
            type="text"
            placeholder="Type your message..."
            :disabled="isSending"
            class="flex-1 px-4 py-3 rounded-lg bg-[#232323] text-white border border-white border-opacity-20 focus:border-white focus:outline-none placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            @click="handleSendMessage"
            :disabled="!newMessage.trim() || isSending"
            class="px-6 py-3 rounded-lg bg-white text-black font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
          >
            Send
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from '#app'
import { definePageMeta } from '#imports'
import { useApi } from '~/src/lib/api'

definePageMeta({
  layout: 'dashboard',
})

const route = useRoute()
const router = useRouter()

const recipientId = ref(Number(route.query.recipient_id))
const addressId = ref(Number(route.query.address_id))
const recipientName = ref('Support Team') // Default name

const newMessage = ref('')
const isSending = ref(false)
const error = ref('')

// Validate query params
onMounted(() => {
  if (!recipientId.value || !addressId.value) {
    console.error('[new-chat] Missing required query params')
    router.replace('/chats')
  }
})

const handleSendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value) return

  isSending.value = true
  error.value = ''

  try {
    console.log('[new-chat] Sending first message to:', recipientId.value)

    const { post } = useApi({ url: '/messages', auth: true })
    const response = await post({
      recipient_id: recipientId.value,
      content: newMessage.value.trim(),
      address_id: addressId.value
    }) as { data: any }

    console.log('[new-chat] Message sent successfully:', response.data)

    // Fetch updated chat list to find the newly created chat
    const { fetch } = useApi({ url: '/messages/chats', auth: true })
    const chatsResponse = await fetch() as { data: any[] }

    // Find the chat with this recipient and address
    const newChat = chatsResponse.data.find(
      (chat: any) => chat.customer_id === recipientId.value && chat.address_id === addressId.value
    )

    if (newChat) {
      console.log('[new-chat] Found new chat:', newChat.id)
      router.replace(`/chats/${newChat.id}`)
    } else {
      console.warn('[new-chat] Could not find new chat, redirecting to chats list')
      router.replace('/chats')
    }
  } catch (err: any) {
    console.error('[new-chat] Error sending message:', err)
    error.value = 'Failed to send message. Please try again.'
    isSending.value = false
  }
}
</script>
