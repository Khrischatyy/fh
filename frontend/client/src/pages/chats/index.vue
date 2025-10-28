<template>
  <div>
    <NuxtLayout
      title="Chats"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <div class="container mx-auto px-2 md:px-4">
        <div class="mb-6 flex justify-between items-center">
          <h1 class="text-2xl font-bold">Chats</h1>
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

        <div v-else-if="filteredChats.length === 0" class="text-center py-8 text-gray-400">
          No chats found
        </div>

        <div v-else class="grid grid-cols-1 gap-4">
          <div
            v-for="chat in filteredChats"
            :key="chat.id"
            class="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors cursor-pointer"
            @click="openChat(chat)"
          >
            <div class="flex justify-between items-start">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
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
    </NuxtLayout>
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '~/src/lib/api'
import { useSessionStore } from '~/src/entities/Session'

type Chat = {
  id: number
  customer_name: string
  address_name: string
  last_message: string
  last_message_time: string
  unread_count: number
}

const router = useRouter()
const chats = ref<Chat[]>([])
const isLoading = ref(false)
const error = ref('')
const searchQuery = ref('')
const session = computed(() => useSessionStore())
const companySlug = computed(() => session.value.brand)

const filteredChats = computed(() => {
  if (!searchQuery.value) return chats.value
  
  const query = searchQuery.value.toLowerCase()
  return chats.value.filter(chat => 
    chat.customer_name.toLowerCase().includes(query) ||
    chat.address_name.toLowerCase().includes(query) ||
    chat.last_message.toLowerCase().includes(query)
  )
})

onMounted(() => {
  fetchChats()
})

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
