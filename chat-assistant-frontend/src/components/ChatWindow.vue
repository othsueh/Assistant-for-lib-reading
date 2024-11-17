<template>
  <div class="chat-window">
    <MessageList />
    <MessageInput />
  </div>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: rgb(197, 148, 199);
}
</style>