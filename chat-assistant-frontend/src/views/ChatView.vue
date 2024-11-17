<template>
  <div class="chat-container">
    <aside class="sidebar">
      <DialogList />
    </aside>
    <main class="main-content">
      <ChatWindow />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import DialogList from '@/components/DialogList.vue'
import ChatWindow from '@/components/ChatWindow.vue'

onMounted(() => {
  console.log('ChatView mounted')
})
</script>

<style>
/* Reset default margins and padding */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  height: 100vh;
  font-family: 'Inika', serif;
}

#app {
  height: 100vh;
}
.inika-regular {
  font-family: "Inika", serif;
  font-weight: 400;
  font-style: normal;
}

.inika-bold {
  font-family: "Inika", serif;
  font-weight: 700;
  font-style: normal;
}

.fira-sans-regular {
  font-family: "Fira Sans", sans-serif;
  font-weight: 400;
  font-style: normal;
}

.fira-sans-medium {
  font-family: "Fira Sans", sans-serif;
  font-weight: 500;
  font-style: normal;
}

</style>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  /* border-right: 1px solid #e2e8f0; */
  background-color: #ae7dac;
  height: 100vh;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
</style>
<!-- <style scoped>
.chat-container {
  display: flex;
  height: 100%;
  width: 100%;
  min-width: 0; /* Add this to prevent flex items from overflowing */
}

.sidebar {
  width: 250px;
  min-width: 250px; /* Add this to prevent shrinking */
  border-right: 1px solid #e2e8f0;
  background-color: #f8fafc;
  height: 100%;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  min-width: 0; /* Add this to prevent overflow */
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
</style> -->