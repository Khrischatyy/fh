<template>
  <div v-if="showPopup" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-black opacity-50" @click="closePopup"></div>
    <div class="relative bg-[#171717] rounded-lg w-[500px] max-h-[70vh] flex flex-col">
      <div class="p-4 border-b border-white border-opacity-20 flex justify-between items-center">
        <h2 class="text-white text-xl font-[BebasNeue]">Chat</h2>
        <button @click="closePopup" class="text-white hover:text-gray-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="messages.length === 0" class="text-center text-gray-400 mt-10">No messages yet. Start the conversation!</div>
        <div v-for="message in messages" :key="message.id" 
             :class="['message mb-4 flex flex-col', message.isOwn ? 'items-end' : 'items-start']">
          <div :class="['message-content', message.isOwn ? 'own-bubble' : 'other-bubble']">
            <span class="sender-label text-xs font-bold block mb-1" v-if="message.isOwn">You</span>
            <span class="sender-label text-xs font-bold block mb-1" v-else>Interlocutor</span>
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
            placeholder="Type a message..."
            class="flex-1 px-3 py-2 rounded-lg bg-[#232323] text-white border border-white border-opacity-20 focus:border-white focus:outline-none placeholder-gray-400"
          />
          <button @click="sendMessage" class="p-2 rounded-lg bg-[#4a90e2] text-white">
            <IconSend class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { useSessionStore } from '~/src/entities/Session'
import IconSend from './IconSend.vue'

const props = defineProps({
  showPopup: {
    type: Boolean,
    required: true
  },
  studioId: {
    type: [String, Number],
    required: true
  },
  recipientId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['closePopup'])

const sessionStore = useSessionStore()
const socket = ref(null)
const messages = ref([])
const newMessage = ref('')
const isConnected = ref(true)

const connectSocket = () => {
  try {
    console.log('[chat] Connecting to WebSocket...')
    const host = import.meta.env.VITE_WEBSOCKET_HOST || 'http://127.0.0.1:6001'
    console.log('[chat] WebSocket host:', host)
    console.log('[chat][debug] sessionStore:', sessionStore)
    console.log('[chat][debug] sessionStore.accessToken:', sessionStore.accessToken)
    const token = sessionStore.accessToken
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
      console.log('[chat][debug] emit get-message-history', {
        addressId: props.studioId,
        recipientId: props.recipientId
      })
      socket.value.emit('get-message-history', {
        addressId: props.studioId,
        recipientId: props.recipientId
      })
    })

    socket.value.on('connect_error', (error) => {
      console.error('[chat] Connection error:', error)
      isConnected.value = false
    })

    socket.value.on('error', (error) => {
      console.error('[chat] Socket error:', error)
    })

    socket.value.on('disconnect', (reason) => {
      console.log('[chat] Disconnected:', reason)
      isConnected.value = false
    })

    socket.value.on('new-message', (message) => {
      console.log('[chat][debug] new-message received:', message)
      messages.value.push({
        ...message,
        text: message.text || message.message || message.content,
        isOwn: Number(message.senderId ?? message.sender_id) === Number(sessionStore.user?.id),
        createdAt: message.createdAt || message.created_at || message.timestamp
      })
      scrollToBottom()
    })

    socket.value.on('message-history', (history) => {
      console.log('[chat][debug] message-history received:', history)
      messages.value = history.map(msg => ({
        ...msg,
        text: msg.text || msg.message || msg.content,
        isOwn: Number(msg.senderId ?? msg.sender_id) === Number(sessionStore.user?.id),
        createdAt: msg.createdAt || msg.created_at || msg.timestamp
      }))
      scrollToBottom()
    })

  } catch (error) {
    console.error('[chat] Error connecting to WebSocket:', error)
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return

  console.log('[chat][debug] emit private-message', {
    recipientId: props.recipientId,
    message: newMessage.value,
    addressId: props.studioId
  })

  socket.value.emit('private-message', {
    recipientId: props.recipientId,
    message: newMessage.value,
    addressId: props.studioId
  })

  newMessage.value = ''
}

const scrollToBottom = () => {
  setTimeout(() => {
    const container = document.querySelector('.overflow-y-auto')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, 100)
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-';
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return '-';
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

const closePopup = () => {
  emit('closePopup')
}

onMounted(() => {
  console.log('[chat][debug] sessionStore.user?.id:', sessionStore.user?.id)
  console.log('[chat][debug] props.recipientId:', props.recipientId)
  console.log('[chat][debug] props.studioId:', props.studioId)
  connectSocket()
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

.message-own {
  margin-left: auto;
}

.message-other {
  margin-right: auto;
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
  border-bottom-left-radius: 15px;
  border-top-right-radius: 15px;
  border-top-left-radius: 15px;
  align-self: flex-end;
}

.other-bubble {
  background: #232323;
  color: #fff;
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

input[type="text"], .message-input {
  color: #fff !important;
  background: #232323 !important;
}
input[type="text"]::placeholder, .message-input::placeholder {
  color: #e0e0e0 !important;
  opacity: 1;
}
</style> 