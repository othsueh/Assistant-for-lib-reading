<template>
  <div class="app">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style scoped>
.app {
  height: 100vh;
  width: 100vw;
  margin: 0;
}
</style>