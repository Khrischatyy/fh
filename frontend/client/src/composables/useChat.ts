import { ref, onUnmounted, nextTick, watch, type Ref } from 'vue'
import { io, type Socket } from 'socket.io-client'
import { useSessionStore } from '~/src/entities/Session'

export interface ChatMessage {
  id: number | string
  text?: string
  message?: string
  content?: string
  senderId?: number
  sender_id?: number
  recipientId?: number
  recipient_id?: number
  isOwn: boolean
  createdAt?: string
  created_at?: string
  timestamp?: string
}

export interface UseChatOptions {
  recipientId: number
  addressId: number
  autoConnect?: boolean
}

export function useChat(options: UseChatOptions) {
  const { recipientId, addressId, autoConnect = true } = options

  const sessionStore = useSessionStore()
  const socket: Ref<Socket | null> = ref(null)
  const messages: Ref<ChatMessage[]> = ref([])
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const error = ref<string | null>(null)

  /**
   * Normalize message fields to consistent structure
   */
  const normalizeMessage = (msg: any): ChatMessage => {
    return {
      ...msg,
      text: msg.text || msg.message || msg.content,
      senderId: msg.senderId ?? msg.sender_id,
      recipientId: msg.recipientId ?? msg.recipient_id,
      isOwn: Number(msg.senderId ?? msg.sender_id) === Number(sessionStore.user?.id),
      createdAt: msg.createdAt || msg.created_at || msg.timestamp
    }
  }

  /**
   * Connect to Socket.io server
   */
  const connect = () => {
    if (socket.value?.connected) {
      console.log('[useChat] Already connected')
      return
    }

    if (isConnecting.value) {
      console.log('[useChat] Connection in progress')
      return
    }

    if (!sessionStore.accessToken) {
      error.value = 'No access token available'
      console.error('[useChat]', error.value)
      return
    }

    try {
      isConnecting.value = true
      error.value = null

      console.log('[useChat] Connecting to WebSocket...')
      const host = window.location.origin
      const token = sessionStore.accessToken

      socket.value = io(host, {
        path: '/socket.io/',
        auth: { token },
        transports: ['websocket', 'polling']
      })

      // Connection successful
      socket.value.on('connect', () => {
        console.log('[useChat] Connected to WebSocket')
        isConnected.value = true
        isConnecting.value = false

        // Load message history
        console.log('[useChat] Requesting message history', { addressId, recipientId })
        socket.value?.emit('get-message-history', {
          addressId,
          recipientId
        })
      })

      // Connection error
      socket.value.on('connect_error', (err) => {
        console.error('[useChat] Connection error:', err)
        isConnected.value = false
        isConnecting.value = false
        error.value = `Connection error: ${err.message}`
      })

      // Disconnected
      socket.value.on('disconnect', (reason) => {
        console.log('[useChat] Disconnected:', reason)
        isConnected.value = false
        isConnecting.value = false
      })

      // Socket error
      socket.value.on('error', (err) => {
        console.error('[useChat] Socket error:', err)
        error.value = typeof err === 'string' ? err : 'Socket error occurred'
      })

      // New message received
      socket.value.on('new-message', (message) => {
        console.log('[useChat] New message received:', message)
        const normalized = normalizeMessage(message)

        // Avoid duplicates by checking if message ID already exists
        const exists = messages.value.some(m => m.id === normalized.id)
        if (!exists) {
          messages.value.push(normalized)
          scrollToBottom()
        }
      })

      // Message history received
      socket.value.on('message-history', (history) => {
        console.log('[useChat] Message history received:', history?.length || 0, 'messages')
        messages.value = (history || []).map(normalizeMessage)
        scrollToBottom()
      })

    } catch (err) {
      console.error('[useChat] Error connecting:', err)
      error.value = 'Failed to connect to chat server'
      isConnecting.value = false
    }
  }

  /**
   * Disconnect from Socket.io server
   */
  const disconnect = () => {
    if (socket.value) {
      console.log('[useChat] Disconnecting...')
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
      isConnecting.value = false
    }
  }

  /**
   * Send a message
   */
  const sendMessage = (messageText: string) => {
    if (!messageText.trim()) {
      console.warn('[useChat] Cannot send empty message')
      return
    }

    if (!socket.value?.connected) {
      console.error('[useChat] Cannot send message: not connected')
      error.value = 'Not connected to chat server'
      return
    }

    console.log('[useChat] Sending message:', { recipientId, addressId, messageText })

    // Emit to server
    socket.value.emit('private-message', {
      recipientId,
      message: messageText,
      addressId
    })

    // Optimistically add to UI
    messages.value.push({
      id: Date.now(),
      text: messageText,
      isOwn: true,
      createdAt: new Date().toISOString()
    })

    scrollToBottom()
  }

  /**
   * Scroll messages container to bottom
   */
  const scrollToBottom = () => {
    nextTick(() => {
      // Try multiple selectors to find messages container
      const container =
        document.querySelector('.messages-container') ||
        document.querySelector('.overflow-y-auto') ||
        document.querySelector('[ref="messagesContainer"]')

      if (container) {
        container.scrollTop = container.scrollHeight
      }
    })
  }

  /**
   * Format timestamp to readable time
   */
  const formatTime = (timestamp?: string) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    if (isNaN(date.getTime())) return ''
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  /**
   * Clear all messages
   */
  const clearMessages = () => {
    messages.value = []
  }

  // Auto-connect if enabled
  if (autoConnect && sessionStore.isAuthorized) {
    connect()
  }

  // Watch for authorization changes and auto-connect if needed
  if (autoConnect) {
    watch(() => sessionStore.isAuthorized, (isAuth) => {
      if (isAuth && !socket.value?.connected) {
        console.log('[useChat] Session authorized, connecting...')
        connect()
      } else if (!isAuth && socket.value?.connected) {
        console.log('[useChat] Session unauthorized, disconnecting...')
        disconnect()
      }
    })
  }

  // Auto-disconnect on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    // State
    socket,
    messages,
    isConnected,
    isConnecting,
    error,

    // Methods
    connect,
    disconnect,
    sendMessage,
    scrollToBottom,
    formatTime,
    clearMessages,
    normalizeMessage
  }
}
