<template>
  <div class="dialog-list">
    <button @click="createDialog" class="new-chat-btn">
      New Chat
    </button>
    <div 
      v-for="dialog in chatStore.dialogs" 
      :key="dialog.id" 
      :class="['dialog-item', { active: dialog.id === chatStore.currentDialogId }]"
      @click="chatStore.setCurrentDialog(dialog.id)"
    >
      Chat: {{ dialog.id }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { onMounted } from 'vue'  
const chatStore = useChatStore()

const createDialog = async () => {
  const name = `Chat ${chatStore.dialogs.length + 1}`
  await chatStore.createNewDialog(name)
}
const loadDialogs = async () => {
  await chatStore.loadDialogs()
}

onMounted(() => {
  loadDialogs()
})

</script>

<style scoped>
.dialog-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.new-chat-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #413b61;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-family: "Fira Sans", sans-serif;
  font-weight: 400;
  transition: background-color 0.2s;
}

.new-chat-btn:hover {
  background-color: #662249;
}

.dialog-item {
  padding: 0.75rem;
  cursor: pointer;
  border-radius: 0.5rem;
  color: #f3dadf;
  transition: background-color 0.2s;
}

.dialog-item:hover {
  background-color: #ed9159;
}

.dialog-item.active {
  background-color: #f1916d;
  font-weight: 500;
}
</style>