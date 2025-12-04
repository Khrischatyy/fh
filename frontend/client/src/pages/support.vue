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
              <span :class="['w-2 h-2 rounded-full', isConnected ? 'bg-green-500' : 'bg-red-500']"></span>
              <span class="text-white/60 text-sm">{{ isConnected ? 'Connected' : 'Connecting...' }}</span>
            </div>
          </div>

          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4">
            <div v-if="messages.length === 0" class="text-center text-gray-400 mt-10">
              No messages yet. Start the conversation with our support team!
            </div>
            <div v-for="message in messages" :key="message.id"
                 :class="['message mb-4 flex flex-col', message.isOwn ? 'items-end' : 'items-start']">
              <div :class="['message-content', message.isOwn ? 'own-bubble' : 'other-bubble']">
                <span class="sender-label text-xs font-bold block mb-1">{{ message.isOwn ? 'You' : 'Support' }}</span>
                {{ message.text || message.message || message.content }}
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
                @keyup.enter="sendMessage"
                type="text"
                placeholder="Type your message..."
                class="flex-1 px-3 py-2 rounded-lg bg-[#232323] text-white border border-white border-opacity-20 focus:border-white focus:outline-none placeholder-gray-400"
              />
              <button
                @click="sendMessage"
                :disabled="!newMessage.trim() || !isConnected"
                class="px-4 py-2 rounded-lg bg-white text-black font-medium disabled:opacity-50 disabled:cursor-not-allowed"
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { io, Socket } from 'socket.io-client'
import { IconLeft } from '~/src/shared/ui/common'
import { navigateTo, definePageMeta, useRuntimeConfig } from '#app'
import { useSessionStore } from '~/src/entities/Session'

definePageMeta({
  layout: 'error',
})

const config = useRuntimeConfig()
const session = useSessionStore()

// Support configuration from environment variables
// Set SUPPORT_USER_ID and SUPPORT_ADDRESS_ID in your .env file
const SUPPORT_USER_ID = Number(config.public.supportUserId) || 1
const SUPPORT_ADDRESS_ID = Number(config.public.supportAddressId) || 1

const socket = ref<Socket | null>(null)
const messages = ref<any[]>([])
const newMessage = ref('')
const isConnected = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

const connectSocket = () => {
  if (!session.isAuthorized) return

  try {
    console.log('[support-chat] Connecting to WebSocket...')
    const host = window.location.origin
    const token = session.accessToken

    socket.value = io(host, {
      path: '/socket.io/',
      auth: { token },
      transports: ['websocket', 'polling']
    })

    socket.value.on('connect', () => {
      console.log('[support-chat] Connected')
      isConnected.value = true
      // Load message history
      socket.value?.emit('get-message-history', {
        addressId: SUPPORT_ADDRESS_ID,
        recipientId: SUPPORT_USER_ID
      })
    })

    socket.value.on('connect_error', (error) => {
      console.error('[support-chat] Connection error:', error)
      isConnected.value = false
    })

    socket.value.on('disconnect', () => {
      console.log('[support-chat] Disconnected')
      isConnected.value = false
    })

    socket.value.on('new-message', (message) => {
      console.log('[support-chat] New message:', message)
      messages.value.push({
        ...message,
        text: message.text || message.message || message.content,
        isOwn: Number(message.senderId ?? message.sender_id) === Number(session.user?.id),
        createdAt: message.createdAt || message.created_at || message.timestamp
      })
      scrollToBottom()
    })

    socket.value.on('message-history', (history) => {
      console.log('[support-chat] History loaded:', history?.length || 0, 'messages')
      messages.value = (history || []).map((msg: any) => ({
        ...msg,
        text: msg.text || msg.message || msg.content,
        isOwn: Number(msg.senderId ?? msg.sender_id) === Number(session.user?.id),
        createdAt: msg.createdAt || msg.created_at || msg.timestamp
      }))
      scrollToBottom()
    })

  } catch (error) {
    console.error('[support-chat] Error:', error)
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !socket.value || !isConnected.value) return

  socket.value.emit('private-message', {
    recipientId: SUPPORT_USER_ID,
    message: newMessage.value,
    addressId: SUPPORT_ADDRESS_ID
  })

  // Optimistically add message to UI
  messages.value.push({
    id: Date.now(),
    text: newMessage.value,
    isOwn: true,
    createdAt: new Date().toISOString()
  })

  newMessage.value = ''
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  if (session.isAuthorized) {
    connectSocket()
  }
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
})
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
