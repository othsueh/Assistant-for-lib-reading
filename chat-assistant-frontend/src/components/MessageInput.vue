<template>
  <div class="message-input">
    <textarea
      v-model="message"
      @keydown.enter.prevent="(e) => {
        console.log('Enter key pressed');
        if (!e.shiftKey) {
          sendMessage();
        }
      }"
      placeholder="Type a message..."
      rows="1"
      ref="textareaRef"
      @input="adjustHeight"
    ></textarea>
    <button 
      @click="(e) => {
        console.log('Send button clicked');
        sendMessage();
      }"
      :disabled="!message.trim() || chatStore.isLoading"
      class="send-button"
    >
      Send
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'

const message = ref('')
const chatStore = useChatStore()
const textareaRef = ref<HTMLTextAreaElement | null>(null)
// Separate handlers for clarity
const handleClick = () => {
  console.log('Button clicked')
  console.log('Message content:', message.value)
  console.log('Store state:', chatStore.$state)
  sendMessage()
}

const handleEnter = (e: KeyboardEvent) => {
  console.log('Enter pressed')
  if (!e.shiftKey) {
    sendMessage()
  }
}

const sendMessage = async () => {
  console.log('MessageInput: Starting sendMessage') // Debug log
  if (!message.value.trim() || chatStore.isLoading){
    console.log('MessageInput: Message is empty or chatStore is loading') // Debug log
    return
  } 
  const messageText = message.value
  console.log('MessageInput: Message to send:', messageText) // Debug log
  try {
    message.value = ''
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
    await chatStore.sendMessage(messageText)
    console.log('MessageInput: Message sent successfully') // Debug log
  } catch (error) {
    console.error('MessageInput: Error sending message:', error) // Debug log
  }
}

const adjustHeight = () => {
  console.log('MessageInput: Adjusting height') // Debug log
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`
  }
}
</script>

<style scoped>
.message-input {
  padding: 1rem;
  display: flex;
  /* gap: 0.5rem; */
  align-items: flex-end;
  background-color: #fda481;
  position: relative;
  margin: 0 8rem 0 8rem;
  border-radius: 1rem 1rem 0 0;
}

textarea {
  flex: 1;
  padding: 0.75rem;
  padding-right: 4rem; /* Make room for the button */
  border: 1px solid #f2b096;
  background-color: #f7c6b3;
  border-radius: 0.5rem;
  resize: none;
  max-height: 150px;
  font-family: inherit;
  font-size: inherit;
  line-height: 1.5;
}

textarea:focus {
  outline: none;
  box-shadow: 0 0 0 2px #f1916d;
}

.send-button {
  position: absolute;
  right: 1.5rem;
  bottom: 1.5rem;
  padding: 0.5rem 1rem;
  background-color: #a34054;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-family: "Fira Sans", sans-serif;
  font-weight: 400;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.send-button:disabled {
  background-color: #aa6d79;
  cursor: not-allowed;
}
</style>