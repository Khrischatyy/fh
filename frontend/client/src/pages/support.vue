<template>
  <div class="w-full min-h-screen bg-black px-5 py-10">
    <div class="flex flex-col gap-10 justify-center items-center">
      <div class="text-center flex flex-col gap-5">
        <h1 class="text-4xl font-bold text-white">Contact Support</h1>
        <p class="text-xl text-white/70">
          Have a question or need help? Chat with our support team.
        </p>
      </div>

      <!-- Not logged in message -->
      <div v-if="!session.isAuthorized" class="max-w-xl w-full text-center">
        <p class="text-white/70 mb-6">
          Please log in to start a conversation with our support team.
        </p>
        <button
          @click="navigateTo('/login')"
          class="w-full max-w-xs h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
        >
          Sign In
        </button>
      </div>

      <!-- Chat Interface for logged in users -->
      <div v-else class="w-full max-w-2xl">
        <!-- Inline Chat (embedded, not modal) -->
        <div class="bg-[#171717] rounded-lg flex flex-col" style="height: 500px;">
          <div class="p-4 border-b border-white border-opacity-20 flex justify-between items-center">
            <h2 class="text-white text-xl font-[BebasNeue]">Support Chat</h2>
            <div class="flex items-center gap-2">
              <span v-if="isConnecting" class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
              <span v-else :class="['w-2 h-2 rounded-full', isConnected ? 'bg-green-500' : 'bg-red-500']"></span>
              <span class="text-white/60 text-sm">
                {{ isConnecting ? 'Connecting...' : (isConnected ? 'Connected' : 'Disconnected') }}
              </span>
            </div>
          </div>

          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 messages-container">
            <div v-if="error" class="text-center text-red-500 mb-4">
              {{ error }}
            </div>
            <div v-if="messages.length === 0" class="text-center text-gray-400 mt-10">
              No messages yet. Start the conversation with our support team!
            </div>
            <div v-for="message in messages" :key="message.id"
                 :class="['message mb-4 flex flex-col', message.isOwn ? 'items-end' : 'items-start']">
              <div :class="['message-content', message.isOwn ? 'own-bubble' : 'other-bubble']">
                <span class="sender-label text-xs font-bold block mb-1">{{ message.isOwn ? 'You' : 'Support' }}</span>
                {{ message.text }}
              </div>
              <div class="message-time">
                {{ formatTime(message.createdAt) }}
              </div>
            </div>
          </div>

          <div class="p-4 border-t border-white border-opacity-20">
            <div class="flex gap-2">
              <input
                v-model="newMessage"
                @keyup.enter="handleSendMessage"
                type="text"
                placeholder="Type your message..."
                :disabled="!isConnected"
                class="flex-1 px-3 py-2 rounded-lg bg-[#232323] text-white border border-white border-opacity-20 focus:border-white focus:outline-none placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button
                @click="handleSendMessage"
                :disabled="!newMessage.trim() || !isConnected"
                class="px-4 py-2 rounded-lg bg-white text-black font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Back to Home -->
      <div class="max-w-xl w-full">
        <button
          @click="navigateTo('/')"
          class="w-full flex justify-center h-11 p-3.5 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
        >
          <icon-left />
          Back to Home
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { IconLeft } from '~/src/shared/ui/common'
import { navigateTo, definePageMeta, useRuntimeConfig } from '#imports'
import { useSessionStore } from '~/src/entities/Session'
import { useChat } from '~/src/composables/useChat'

definePageMeta({
  layout: 'error',
})

const config = useRuntimeConfig()
const session = useSessionStore()

// Support configuration from environment variables
const SUPPORT_USER_ID = Number(config.public.supportUserId) || 1
const SUPPORT_ADDRESS_ID = Number(config.public.supportAddressId) || 4

const newMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// Use the chat composable
const {
  messages,
  isConnected,
  isConnecting,
  error,
  sendMessage,
  formatTime
} = useChat({
  recipientId: SUPPORT_USER_ID,
  addressId: SUPPORT_ADDRESS_ID,
  autoConnect: true // Auto-connect when authorized
})

const handleSendMessage = () => {
  if (!newMessage.value.trim() || !isConnected.value) return

  sendMessage(newMessage.value)
  newMessage.value = ''
}
</script>

<style scoped>
.message {
  max-width: 80%;
}

.message-content {
  padding: 8px 12px;
  border-radius: 15px;
  max-width: 320px;
  word-break: break-word;
  margin-bottom: 2px;
}

.own-bubble {
  background: #4a90e2;
  color: #fff !important;
  border-bottom-right-radius: 4px;
}

.other-bubble {
  background: #232323;
  color: #fff;
  border-bottom-left-radius: 4px;
}

.sender-label {
  opacity: 0.7;
}

.message-time {
  font-size: 0.75rem;
  color: #888;
  margin-top: 2px;
}
</style>
