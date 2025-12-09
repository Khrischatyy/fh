<template>
  <div v-if="showPopup" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-black opacity-50" @click="closePopup"></div>
    <div class="relative bg-[#171717] rounded-lg w-[500px] max-w-[95vw] max-h-[70vh] flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-white border-opacity-20 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <h2 class="text-white text-xl font-[BebasNeue]">Chat</h2>
          <div v-if="isConnecting" class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
            <span class="text-white/60 text-xs">Connecting...</span>
          </div>
          <div v-else-if="isConnected" class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            <span class="text-white/60 text-xs">Connected</span>
          </div>
          <div v-else class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-red-500"></span>
            <span class="text-white/60 text-xs">Disconnected</span>
          </div>
        </div>
        <button @click="closePopup" class="text-white hover:text-gray-300 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Messages -->
      <div class="flex-1 overflow-y-auto p-4 messages-container">
        <div v-if="messages.length === 0" class="text-center text-gray-400 mt-10">
          No messages yet. Start the conversation!
        </div>
        <div v-for="message in messages" :key="message.id"
             :class="['message mb-4 flex flex-col', message.isOwn ? 'items-end' : 'items-start']">
          <div :class="['message-content', message.isOwn ? 'own-bubble' : 'other-bubble']">
            <span class="sender-label text-xs font-bold block mb-1">
              {{ message.isOwn ? 'You' : 'Interlocutor' }}
            </span>
            {{ message.text }}
          </div>
          <div class="message-time">
            {{ formatTime(message.createdAt) }}
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="p-4 border-t border-white border-opacity-20">
        <div v-if="error" class="mb-2 text-red-500 text-sm">{{ error }}</div>
        <div class="flex gap-2">
          <input
            v-model="newMessage"
            @keyup.enter="handleSendMessage"
            type="text"
            placeholder="Type a message..."
            :disabled="!isConnected"
            class="flex-1 px-3 py-2 rounded-lg bg-[#232323] text-white border border-white border-opacity-20 focus:border-white focus:outline-none placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            @click="handleSendMessage"
            :disabled="!newMessage.trim() || !isConnected"
            class="p-2 rounded-lg bg-[#4a90e2] text-white hover:bg-[#3a7fc2] transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#4a90e2]"
          >
            <IconSend class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useChat } from '~/src/composables/useChat'
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

const newMessage = ref('')

// Use the chat composable
const {
  messages,
  isConnected,
  isConnecting,
  error,
  sendMessage,
  formatTime,
  connect,
  disconnect
} = useChat({
  recipientId: Number(props.recipientId),
  addressId: Number(props.studioId),
  autoConnect: false // Manual control
})

// Watch for popup visibility to connect/disconnect
watch(() => props.showPopup, (visible) => {
  if (visible) {
    connect()
  } else {
    disconnect()
  }
}, { immediate: true })

const handleSendMessage = () => {
  if (!newMessage.value.trim() || !isConnected.value) return

  sendMessage(newMessage.value)
  newMessage.value = ''
}

const closePopup = () => {
  emit('closePopup')
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
