<template>
  <div class="app">
    <Sidebar
      :sessions="sessions"
      :currentSessionId="currentSessionId"
      @select-session="onSelectSession"
      @new-chat="onNewChat"
      @delete-session="onDeleteSession"
    />
    <ChatView
      :key="currentSessionId"
      :sessionId="currentSessionId"
      @session-created="onSessionCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import ChatView from './components/ChatView.vue'
import { fetchSessions, deleteSession } from './api/chat.js'

const sessions = ref([])
const currentSessionId = ref(null)

onMounted(async () => {
  try {
    sessions.value = await fetchSessions()
  } catch {
    sessions.value = []
  }
})

function onNewChat() {
  currentSessionId.value = null
}

function onSelectSession(id) {
  currentSessionId.value = id
}

async function onSessionCreated(sid) {
  currentSessionId.value = sid
  try {
    sessions.value = await fetchSessions()
  } catch {}
}

async function onDeleteSession(id) {
  try {
    await deleteSession(id)
    if (currentSessionId.value === id) {
      currentSessionId.value = null
    }
    sessions.value = await fetchSessions()
  } catch {}
}
</script>

<style scoped>
.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
</style>
