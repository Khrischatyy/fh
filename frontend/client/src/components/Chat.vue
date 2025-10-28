<template>
  <div class="chat-container">
    <div class="chat-header" @click="toggleChat">
      <div class="flex items-center gap-2">
        <IconChat class="w-6 h-6" />
        <span class="font-[BebasNeue] text-2xl text-white">Chat</span>
      </div>
    </div>
    
    <div v-if="isOpen" class="chat-body">
      <div class="messages-container" ref="messagesContainer">
        <div v-for="message in messages" :key="message.id" 
             :class="['message', message.isOwn ? 'message-own' : 'message-other']">
          <div class="message-content">
            {{ message.text }}
          </div>
          <div class="message-time">
            {{ formatTime(message.timestamp) }}
          </div>
        </div>
      </div>
      
      <div class="input-container">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage"
          type="text" 
          placeholder="Type a message..."
          class="message-input"
        />
        <button @click="sendMessage" class="send-button">
          <IconSend class="w-6 h-6" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { useSessionStore } from '~/src/entities/Session'

const props = defineProps({
  studioId: {
    type: [String, Number],
    required: true
  }
})

const sessionStore = useSessionStore()
const socket = ref(null)
const messages = ref([])
const newMessage = ref('')
const isOpen = ref(false)
const messagesContainer = ref(null)

const connectSocket = () => {
  const protocol = window.location.protocol
  const host = window.location.hostname
  const port = '6001'
  
  socket.value = io(`${protocol}//${host}:${port}`, {
    auth: {
      token: sessionStore.token
    }
  })

  socket.value.on('connect', () => {
    console.log('Connected to chat server')
    socket.value.emit('join', { studioId: props.studioId })
  })

  socket.value.on('message', (message) => {
    messages.value.push({
      ...message,
      isOwn: message.userId === sessionStore.user?.id
    })
    scrollToBottom()
  })
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return

  socket.value.emit('message', {
    text: newMessage.value,
    studioId: props.studioId
  })

  newMessage.value = ''
}

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 100)
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

onMounted(() => {
  connectSocket()
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
})
</script>

<style scoped>
.chat-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  width: 350px;
  background: #171717;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.chat-header {
  padding: 15px;
  background: #000;
  border-radius: 10px 10px 0 0;
  cursor: pointer;
}

.chat-body {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.message {
  margin-bottom: 10px;
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
  background: #2a2a2a;
  color: white;
}

.message-own .message-content {
  background: #4a90e2;
}

.message-time {
  font-size: 0.75rem;
  color: #888;
  margin-top: 4px;
}

.input-container {
  padding: 15px;
  display: flex;
  gap: 10px;
  background: #000;
  border-radius: 0 0 10px 10px;
}

.message-input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid #333;
  background: #2a2a2a;
  color: white;
}

.send-button {
  padding: 8px;
  border-radius: 50%;
  background: #4a90e2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 