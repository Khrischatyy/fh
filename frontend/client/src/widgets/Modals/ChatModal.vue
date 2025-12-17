<template>
  <!-- Кнопка для открытия модального окна чата -->
  <div>
    <button @click="openChatModal" class="bg-white text-black py-2 px-[10px] rounded-[10px] w-[71px] md:w-full h-[43px] flex items-center justify-center text-[14px] leading-[17px] tracking-[0.04em]">
      Open Chat
    </button>

    <!-- Модальное окно чата с использованием Popup -->
    <Popup
      :open="isChatModalOpen"
      @close="closeChatModal"
      title="Chat with {{ client?.firstname }}"
      modalContentClass="w-[500px] max-w-[95vw] max-h-[70vh] h-[630px]"
    >
      <template #body>
        <div class="chat-modal-body flex flex-col bg-[#1a1a1a] rounded-lg overflow-hidden h-full">
          <!-- Область сообщений -->
          <div ref="messagesContainer" class="messages-area flex-1 overflow-y-auto p-4 bg-gray-100">
            <div v-for="(message, index) in messages" :key="index" :class="['message', message.isOwner ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black']">
              <div class="message-bubble rounded-lg px-4 py-2 mb-2">
                <p class="message-text">{{ message.text }}</p>
                <small class="message-time text-xs">{{ message.time }}</small>
              </div>
            </div>
          </div>

          <!-- Поле ввода и кнопка отправки -->
          <div class="input-area flex items-center p-4 bg-white border-t border-gray-300">
            <input
                v-model="newMessage"
                @keyup.enter="sendMessage"
                type="text"
                placeholder="Type a message..."
                class="flex-1 px-4 py-2 border border-gray-300 rounded-l focus:outline-none focus:border-blue-500"
            />
            <button @click="sendMessage" class="px-4 py-2 bg-blue-600 text-white rounded-r hover:bg-blue-500">
              Send
            </button>
          </div>
        </div>
      </template>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import {Popup} from "~/src/shared/ui/components"

const props = defineProps<{ client: { firstname: string } }>();

// Управление состоянием модального окна
const isChatModalOpen = ref(false);
const messages = ref([
  { text: "Hello, how can I help you?", time: "10:00 AM", isOwner: true },
  { text: "I’d like to book a session.", time: "10:02 AM", isOwner: false }
]);
const newMessage = ref("");
const messagesContainer = ref<HTMLElement | null>(null);

function openChatModal() {
  isChatModalOpen.value = true;
  scrollToBottom();
}

function closeChatModal() {
  isChatModalOpen.value = false;
}

function sendMessage() {
  if (newMessage.value.trim() === "") return;

  // Добавить новое сообщение
  messages.value.push({
    text: newMessage.value,
    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    isOwner: false
  });
  newMessage.value = "";
  scrollToBottom();
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

onMounted(scrollToBottom);
</script>

<style scoped>
.chat-modal-body {
  display: flex;
  flex-direction: column;
}

.messages-area {
  overflow-y: auto;
  padding: 1rem;
  background-color: #f3f4f6;
}

.message-bubble {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  max-width: 70%;
}

.message {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}

.message-time {
  align-self: flex-end;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  opacity: 0.6;
}

.input-area {
  border-top: 1px solid #e5e7eb;
}

.input-area input {
  border-radius: 0.25rem 0 0 0.25rem;
}

.input-area button {
  border-radius: 0 0.25rem 0.25rem 0;
}
</style>
