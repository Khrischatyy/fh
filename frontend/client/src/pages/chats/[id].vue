<template>
  <div class="container mx-auto px-2 md:px-4 h-full flex flex-col" style="height: calc(100vh - 100px);">
        <!-- Header -->
        <div class="py-4 border-b border-gray-700 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <button @click="router.back()" class="text-gray-400 hover:text-white">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div v-if="chat?.customer_photo" class="w-10 h-10 rounded-full overflow-hidden flex-shrink-0">
              <img :src="chat.customer_photo" :alt="chat.customer_name" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
              <span class="text-white font-semibold">{{ getInitials(chat?.customer_name || '') }}</span>
            </div>
            <div>
              <h2 class="font-semibold text-white">{{ chat?.customer_name }}</h2>
              <p class="text-sm text-gray-400">{{ chat?.address_name }}</p>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div
          ref="messagesContainer"
          class="flex-1 overflow-y-auto py-4 space-y-4 flex flex-col-reverse"
          @scroll="handleScroll"
        >
          <div v-if="isLoading" class="flex justify-center items-center py-8">
            <div class="spinner"></div>
          </div>

          <div v-else-if="error" class="text-red-500 text-center py-8">
            {{ error }}
          </div>

          <template v-else>
            <div v-for="message in [...messages].reverse()" :key="message.id"
                 :class="[
                   'flex mb-4',
                   message.sender_id === currentUserId ? 'justify-end' : 'justify-start'
                 ]"
            >
              <div class="flex flex-col max-w-[80%]" :class="message.sender_id === currentUserId ? 'items-end' : 'items-start'">
                <div
                  :class="[
                    'message-content p-3 word-break-break-word',
                    message.sender_id === currentUserId
                      ? 'own-bubble bg-[#4a90e2] text-white'
                      : 'other-bubble bg-[#232323] text-white'
                  ]"
                >
                  <span class="sender-label text-xs font-bold block mb-1" v-if="message.sender_id === currentUserId">You</span>
                  <span class="sender-label text-xs font-bold block mb-1" v-else>{{ chat?.customer_name || 'User' }}</span>
                  <p class="text-sm">{{ message.text }}</p>
                </div>
                <p class="message-time text-xs mt-1 text-gray-400">
                  {{ formatTime(message.created_at) }}
                </p>
              </div>
            </div>
          </template>
        </div>

        <!-- Input -->
        <div class="border-t border-gray-700 p-4">
          <form @submit.prevent="sendMessage" class="flex space-x-4">
            <input
              v-model="newMessage"
              type="text"
              placeholder="Type a message..."
              class="flex-1 bg-[#232323] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-white border-opacity-20"
              :disabled="isSending"
            />
            <button
              type="submit"
              class="bg-[#4a90e2] text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
              :disabled="!newMessage.trim() || isSending"
            >
              <span v-if="!isSending">Send</span>
              <div v-else class="spinner-small"></div>
            </button>
          </form>
        </div>
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

.spinner-small {
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-left-color: #ffffff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.message-content {
  border-radius: 15px;
  max-width: 320px;
  word-break: break-word;
  margin-bottom: 2px;
}

.own-bubble {
  border-bottom-right-radius: 4px;
  border-bottom-left-radius: 15px;
  border-top-right-radius: 15px;
  border-top-left-radius: 15px;
  align-self: flex-end;
}

.other-bubble {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 15px;
  border-top-right-radius: 15px;
  border-top-left-radius: 15px;
  align-self: flex-start;
}

.sender-label {
  opacity: 0.7;
  margin-bottom: 2px;
}

.message-time {
  font-size: 0.75rem;
  color: #888;
  margin-top: 2px;
  margin-bottom: 8px;
}

/* Hide scrollbar but keep functionality */
.overflow-y-auto {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.overflow-y-auto::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
</style>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { definePageMeta } from '#imports'
import { useApi } from '~/src/lib/api'
import { useSessionStore } from '~/src/entities/Session'
import { io } from 'socket.io-client'

definePageMeta({
  layout: 'dashboard',
})

type Message = {
  id: number
  text: string
  sender_id: number
  recipient_id: number
  address_id: number
  is_read: boolean
  created_at: string
  updated_at: string
}

type ChatResponse = {
  id: string
  customer_name: string
  customer_photo?: string
  address_name: string
  customer_id: string
  address_id: number
  messages: Message[]
}

type Chat = {
  id: number
  customer_name: string
  customer_photo?: string
  address_name: string
  customer_id: number
  address_id: number
}

const route = useRoute()
const router = useRouter()
const chatId = computed(() => route.params.id as string)
const messagesContainer = ref<HTMLElement | null>(null)
const messages = ref<Message[]>([])
const chat = ref<Chat | null>(null)
const newMessage = ref('')
const isLoading = ref(true)
const isSending = ref(false)
const error = ref('')
const page = ref(1)
const hasMore = ref(true)
const session = computed(() => useSessionStore())
const currentUserId = computed(() => session.value.user?.id)
const socket = ref<any>(null)
const isConnected = ref(false)

const connectSocket = () => {
  try {
    console.log('[chat] Connecting to WebSocket...')
    // Use relative URL to connect through Caddy proxy
    // This works both in dev (localhost) and production
    const host = window.location.origin
    console.log('[chat] WebSocket host:', host)
    const token = session.value.accessToken
    console.log('[chat] Using token:', token)

    socket.value = io(host, {
      path: '/socket.io/',
      auth: {
        token: token
      },
      transports: ['websocket', 'polling']
    })

    socket.value.on('connect', () => {
      console.log('[chat] Connected to WebSocket')
      isConnected.value = true
      // Load message history when connected
      if (chat.value) {
        console.log('[chat][debug] emit get-message-history', {
          addressId: chat.value.address_id,
          recipientId: chat.value.customer_id
        })
        socket.value.emit('get-message-history', {
          addressId: chat.value.address_id,
          recipientId: chat.value.customer_id
        })
      }
    })

    socket.value.on('connect_error', (error: any) => {
      console.error('[chat] Connection error:', error)
      isConnected.value = false
    })

    socket.value.on('error', (error: any) => {
      console.error('[chat] Socket error:', error)
    })

    socket.value.on('disconnect', (reason: string) => {
      console.log('[chat] Disconnected:', reason)
      isConnected.value = false
    })

    socket.value.on('new-message', (message: any) => {
      console.log('[chat][debug] new-message received:', message)

      // Normalize field names (Socket.io sends "message", we expect "text")
      const normalizedMessage: Message = {
        id: message.id,
        text: message.message || message.content || message.text || '',
        sender_id: message.senderId || message.sender_id,
        recipient_id: message.recipientId || message.recipient_id,
        address_id: message.addressId || message.address_id,
        is_read: message.is_read || false,
        created_at: message.createdAt || message.created_at,
        updated_at: message.updatedAt || message.updated_at || message.createdAt || message.created_at
      }

      // Deduplicate: check if message already exists
      const exists = messages.value.some(m => m.id === normalizedMessage.id)
      if (!exists) {
        messages.value.push(normalizedMessage)
        console.log('Added new message from Socket.io')
        nextTick(() => scrollToBottom())
      } else {
        console.log('Message already exists, skipping duplicate')
      }
    })

    socket.value.on('message-history', (history: any[]) => {
      console.log('[chat][debug] message-history received:', history)
      // Normalize messages from Socket.io (API returns "content", we expect "text")
      messages.value = (history || []).map((msg: any) => ({
        id: msg.id,
        text: msg.content || msg.text || msg.message || '',
        sender_id: msg.sender_id,
        recipient_id: msg.recipient_id,
        address_id: msg.address_id,
        is_read: msg.is_read || false,
        created_at: msg.created_at,
        updated_at: msg.updated_at
      }))
      nextTick(() => scrollToBottom())
    })

  } catch (error) {
    console.error('[chat] Error connecting to WebSocket:', error)
  }
}

onMounted(() => {
  fetchChatDetails()
  connectSocket()
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
})

const fetchChatDetails = async () => {
  isLoading.value = true
  error.value = ''

  try {
    // Using POST request to get chat details with the user ID
    const { post } = useApi({
      url: `/messages/chats/${chatId.value}`,
      auth: true
    })

    const response = await post({}) as { data: ChatResponse }
    const chatData = response.data

    chat.value = {
      id: Number(chatData.id),
      customer_name: chatData.customer_name,
      customer_photo: chatData.customer_photo,
      address_name: chatData.address_name,
      customer_id: Number(chatData.customer_id),
      address_id: chatData.address_id
    }

    if (chatData.messages && Array.isArray(chatData.messages)) {
      // Normalize messages from API (API returns "content", we expect "text")
      messages.value = chatData.messages.map((msg: any) => ({
        id: msg.id,
        text: msg.content || msg.text || msg.message || '',
        sender_id: msg.sender_id,
        recipient_id: msg.recipient_id,
        address_id: msg.address_id,
        is_read: msg.is_read || false,
        created_at: msg.created_at,
        updated_at: msg.updated_at
      }))
      nextTick(() => scrollToBottom())
    }
  } catch (err) {
    console.error('Error fetching chat details:', err)
    error.value = 'Failed to load chat details'
  } finally {
    isLoading.value = false
  }
}

const fetchMessages = async (isInitial = false) => {
  if (isLoading.value) return

  if (isInitial) {
    page.value = 1
    hasMore.value = true
  }

  isLoading.value = true

  try {
    // If using pagination in the future, you can implement it here
    // Currently, all messages are returned from the chatDetails endpoint
  } catch (err) {
    console.error('Error fetching messages:', err)
    error.value = 'Failed to load messages'
  } finally {
    isLoading.value = false
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value || !chat.value) return

  isSending.value = true
  const messageText = newMessage.value.trim()
  newMessage.value = '' // Clear input immediately

  try {
    if (!socket.value || !socket.value.connected) {
      // Fallback to API if Socket.io is not connected
      console.log('[chat] Socket.io not connected, using API fallback')
      const { post } = useApi({
        url: '/messages',
        auth: true
      })

      const messageData = {
        recipient_id: parseInt(String(chat.value.customer_id), 10),
        content: messageText,
        address_id: parseInt(String(chat.value.address_id), 10)
      }

      const response = await post(messageData)
      console.log('[chat] Message sent via API fallback:', response)

      // Add to local UI since we won't get Socket.io broadcast
      if (response && response.data) {
        const savedMessage = response.data
        const normalizedMessage: Message = {
          id: savedMessage.id,
          text: savedMessage.content || savedMessage.text || '',
          sender_id: savedMessage.sender_id,
          recipient_id: savedMessage.recipient_id,
          address_id: savedMessage.address_id,
          is_read: savedMessage.is_read || false,
          created_at: savedMessage.created_at,
          updated_at: savedMessage.updated_at
        }

        const exists = messages.value.some(m => m.id === normalizedMessage.id)
        if (!exists) {
          messages.value.push(normalizedMessage)
        }
      }
    } else {
      // Primary path: Send via Socket.io
      console.log('[chat] Sending message via Socket.io')
      socket.value.emit('private-message', {
        recipientId: parseInt(String(chat.value.customer_id), 10),
        addressId: parseInt(String(chat.value.address_id), 10),
        message: messageText
      })
      console.log('[chat] Message emitted via Socket.io')
      // Message will be added to UI when we receive 'new-message' event
    }

    nextTick(() => scrollToBottom())
  } catch (err) {
    console.error('[chat] Error sending message:', err)
    error.value = 'Failed to send message'
    // Restore message text if sending failed
    newMessage.value = messageText
  } finally {
    isSending.value = false
  }
}

const handleScroll = () => {
  if (!messagesContainer.value) return

  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  // With flex-col-reverse, we load more when reaching the end (top of the reversed view)
  if (Math.abs(scrollHeight - clientHeight - scrollTop) < 10 && hasMore.value) {
    fetchMessages(false)
  }
}

const scrollToBottom = () => {
  if (!messagesContainer.value) return
  // With flex-col-reverse, scrollTop = 0 is already at the bottom (latest messages)
  messagesContainer.value.scrollTop = 0
}

const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}
</script>
