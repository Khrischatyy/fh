<template>
  <div class="container mx-auto px-2 md:px-4">
        <div class="mb-6 flex justify-between items-center">
          <div class="flex items-center space-x-4">
            <div class="relative">
              <input
                type="text"
                v-model="searchQuery"
                placeholder="Search chats..."
                class="bg-gray-800 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="flex justify-center items-center py-8">
          <div class="spinner"></div>
        </div>

        <div v-else-if="error" class="text-red-500 text-center py-8">
          {{ error }}
        </div>

        <div v-else-if="filteredChats.length === 0 && !supportChat" class="text-center py-8 text-gray-400">
          No chats found
        </div>

        <div v-else class="grid grid-cols-1 gap-4">
          <!-- Support Chat (Always at Top) -->
          <div v-if="supportChat" class="mb-2">
            <h3 class="text-sm text-gray-400 mb-2 px-2">Support</h3>
            <div
              @click="openChat(supportChat)"
              class="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-2 border-blue-500/30 rounded-lg p-4 cursor-pointer hover:border-blue-500/50 transition-all relative"
            >
              <!-- Support Badge Icon -->
              <div class="absolute top-3 right-3">
                <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
                </svg>
              </div>

              <div class="flex items-start gap-3">
                <div v-if="supportChat.customer_photo" class="w-12 h-12 rounded-full overflow-hidden flex-shrink-0">
                  <img :src="supportChat.customer_photo" :alt="supportChat.customer_name" class="w-full h-full object-cover" />
                </div>
                <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                  {{ getInitials(supportChat.customer_name || 'Support Team') }}
                </div>
                <div class="flex-1 min-w-0 pr-8">
                  <h3 class="font-semibold text-white text-lg">{{ supportChat.customer_name || 'Support Team' }}</h3>
                  <p class="text-sm text-gray-300 truncate mt-1">
                    {{ supportChat.last_message || 'Start a conversation with our support team' }}
                  </p>
                  <div class="flex items-center gap-2 mt-2">
                    <p class="text-xs text-gray-400">
                      {{ formatTime(supportChat.last_message_time) }}
                    </p>
                    <div v-if="supportChat.unread_count > 0" class="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {{ supportChat.unread_count }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Regular Chats -->
          <div v-if="filteredChats.length > 0">
            <h3 class="text-sm text-gray-400 mb-2 px-2">Your Chats</h3>
            <div
              v-for="chat in filteredChats"
              :key="chat.id"
              class="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors cursor-pointer"
              @click="openChat(chat)"
            >
              <div class="flex justify-between items-start">
                <div class="flex items-center space-x-3">
                  <div v-if="chat.customer_photo" class="w-10 h-10 rounded-full overflow-hidden flex-shrink-0">
                    <img :src="chat.customer_photo" :alt="chat.customer_name" class="w-full h-full object-cover" />
                  </div>
                  <div v-else class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                    <span class="text-white font-semibold">{{ getInitials(chat.customer_name) }}</span>
                  </div>
                  <div>
                    <h3 class="font-semibold text-white">{{ chat.customer_name }}</h3>
                    <p class="text-gray-400 text-sm">{{ chat.address_name }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm text-gray-400">{{ formatTime(chat.last_message_time) }}</div>
                  <div v-if="chat.unread_count > 0" class="mt-1">
                    <span class="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                      {{ chat.unread_count }} new
                    </span>
                  </div>
                </div>
              </div>
              <p class="mt-2 text-gray-300 line-clamp-1">{{ chat.last_message }}</p>
            </div>
          </div>
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRuntimeConfig, definePageMeta } from '#imports'
import { useApi } from '~/src/lib/api'
import { useSessionStore } from '~/src/entities/Session'
import { io, Socket } from 'socket.io-client'

definePageMeta({
  layout: 'dashboard',
})

type Chat = {
  id: number
  customer_id: number
  customer_name: string
  customer_photo?: string
  address_name: string
  last_message: string
  last_message_time: string
  unread_count: number
}

const router = useRouter()
const config = useRuntimeConfig()
const chats = ref<Chat[]>([])
const isLoading = ref(false)
const error = ref('')
const searchQuery = ref('')
const session = computed(() => useSessionStore())
const companySlug = computed(() => session.value.brand)
const socket = ref<Socket | null>(null)

const SUPPORT_USER_ID = Number(config.public.supportUserId) || 1

// Separate support chat from regular chats
const supportChat = computed(() =>
  chats.value.find(chat => chat.customer_id === SUPPORT_USER_ID)
)

const regularChats = computed(() =>
  chats.value.filter(chat => chat.customer_id !== SUPPORT_USER_ID)
)

// Apply search filter to regular chats only
const filteredChats = computed(() => {
  if (!searchQuery.value) return regularChats.value

  const query = searchQuery.value.toLowerCase()
  return regularChats.value.filter(chat =>
    chat.customer_name.toLowerCase().includes(query) ||
    chat.address_name.toLowerCase().includes(query) ||
    chat.last_message.toLowerCase().includes(query)
  )
})

onMounted(() => {
  fetchChats()
  connectSocket()
})

onUnmounted(() => {
  disconnectSocket()
})

const connectSocket = () => {
  if (!session.value.isAuthorized) return

  const sessionStore = useSessionStore()
  const token = sessionStore.token

  console.log('[chats-list] Connecting to Socket.io...')

  socket.value = io(window.location.origin, {
    path: '/socket.io/',
    auth: { token: `Bearer ${token}` },
    transports: ['websocket', 'polling']
  })

  socket.value.on('connect', () => {
    console.log('[chats-list] Connected to Socket.io')
  })

  socket.value.on('new-message', (message: any) => {
    console.log('[chats-list] New message received:', message)

    // Find the chat for this message
    const chatIndex = chats.value.findIndex(
      chat => chat.id === message.senderId || chat.id === message.recipientId
    )

    if (chatIndex !== -1) {
      // Update existing chat
      const chat = chats.value[chatIndex]
      chat.last_message = message.content || message.text || message.message || ''
      chat.last_message_time = message.createdAt || message.created_at || new Date().toISOString()

      // Increment unread count if message is from other user
      const currentUserId = sessionStore.user?.id
      if (message.senderId !== currentUserId && message.sender_id !== currentUserId) {
        chat.unread_count = (chat.unread_count || 0) + 1
      }

      // Move chat to top by re-sorting
      chats.value.sort((a, b) => {
        const timeA = new Date(a.last_message_time).getTime()
        const timeB = new Date(b.last_message_time).getTime()
        return timeB - timeA
      })
    } else {
      // New chat - refresh the list
      fetchChats()
    }
  })

  socket.value.on('disconnect', () => {
    console.log('[chats-list] Disconnected from Socket.io')
  })

  socket.value.on('connect_error', (err: any) => {
    console.error('[chats-list] Socket.io connection error:', err)
  })
}

const disconnectSocket = () => {
  if (socket.value) {
    console.log('[chats-list] Disconnecting from Socket.io')
    socket.value.disconnect()
    socket.value = null
  }
}

const fetchChats = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const { fetch } = useApi({
      url: '/messages/chats',
      auth: true
    })

    const response = await fetch() as { data: Chat[] }
    chats.value = response.data
  } catch (err) {
    console.error('Error fetching chats:', err)
    error.value = 'Failed to load chats. Please try again later.'
  } finally {
    isLoading.value = false
  }
}

const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString()
}

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const openChat = (chat: Chat) => {
  router.push(`/chats/${chat.id}`)
}
</script>
