<template>
  <div class="chat-view">
    <div v-if="messages.length === 0 && !streaming" class="empty-state">
      <h2>🤖 Ollama AI Chat</h2>
      <p>选择一个对话或新建一个开始聊天</p>
    </div>
    <MessageList :messages="messages" :streaming="streaming" />
    <ChatInput :disabled="streaming" @send="onSend" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import MessageList from './MessageList.vue'
import ChatInput from './ChatInput.vue'
import { streamChat } from '../api/chat.js'
import { fetchMessages } from '../api/chat.js'

const props = defineProps({
  sessionId: { type: Number, default: null },
})
const emit = defineEmits(['session-created'])

const messages = ref([])
const streaming = ref(false)

// 切换会话时清空消息（后续可扩展为按 sessionId 加载历史）
watch(() => props.sessionId, async(newId) => {
  if (newId){
    try{
      messages.value = await fetchMessages(newId)
    } catch {
      messages.value = []
    }
  } else{
    messages.value = []
  }
}, { immediate: true })

async function onSend(message) {
  messages.value.push({ role: 'user', content: message })
  streaming.value = true

  // 助手消息占位
  const aiIdx = messages.value.length
  messages.value.push({ role: 'assistant', content: '' })

  await streamChat(
    message,
    props.sessionId,
    // onChunk
    (chunk) => {
      messages.value[aiIdx].content += chunk
    },
    // onDone
    (sid) => {
      streaming.value = false
      if (!props.sessionId) {
        emit('session-created', sid)
      }
    },
    // onError
    (err) => {
      streaming.value = false
      messages.value[aiIdx].content = `❌ 错误: ${err}`
    }
  )
}
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100vh;
  background: #fff;
}
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}
.empty-state h2 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #6b7280;
}
</style>
