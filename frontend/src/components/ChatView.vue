<template>
  <div class="chat-view">
    <div v-if="messages.length === 0 && !streaming" class="empty-state">
      <h2>🤖 Ollama AI Chat</h2>
      <p>选择一个对话或新建一个开始聊天</p>
    </div>
    <MessageList :messages="messages" :streaming="streaming" />
    <!-- RAG 工具栏 -->
    <div class="rag-bar">
      <label class="rag-toggle" title="开启后 AI 会基于你上传的文档回答">
        <input type="checkbox" v-model="ragEnabled" :disabled="streaming" />
        <span class="toggle-label">📚 知识库</span>
      </label>
      <button
        v-if="ragEnabled"
        class="upload-btn"
        :disabled="streaming"
        @click="$refs.fileInput.click()"
      >📎 {{ uploadedFile || '上传文档' }}</button>
      <span v-if="ragEnabled && chunkCount > 0" class="stat">已索引 {{ chunkCount }} 块</span>
      <input
        ref="fileInput"
        type="file"
        accept=".txt,.md,.csv,.json"
        style="display:none"
        @change="onFileChange"
      />
    </div>
    <ChatInput :disabled="streaming" @send="onSend" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import MessageList from './MessageList.vue'
import ChatInput from './ChatInput.vue'
import { streamChat, fetchMessages, uploadDocument, fetchRagStats } from '../api/chat.js'

const props = defineProps({
  sessionId: { type: Number, default: null },
})
const emit = defineEmits(['session-created'])

const messages = ref([])
const streaming = ref(false)
const ragEnabled = ref(false)
const uploadedFile = ref('')
const chunkCount = ref(0)

onMounted(async () => {
  try {
    const stats = await fetchRagStats()
    chunkCount.value = stats.total_chunks || 0
  } catch {}
})

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
    },
    // rag
    ragEnabled.value
  )
}

async function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadedFile.value = '上传中...'
  try {
    const result = await uploadDocument(file)
    uploadedFile.value = file.name
    chunkCount.value = result.chunks
  } catch (err) {
    uploadedFile.value = ''
    alert('上传失败: ' + err.message)
  }
  e.target.value = ''
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

/* RAG 工具栏 */
.rag-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-top: 1px solid #e5e7eb;
  background: #fafafa;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}
.rag-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
  font-size: 13px;
}
.rag-toggle input[type="checkbox"] {
  accent-color: #4f46e5;
}
.toggle-label {
  color: #374151;
}
.upload-btn {
  padding: 4px 12px;
  background: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}
.upload-btn:hover {
  background: #d1d5db;
}
.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.stat {
  color: #6b7280;
  font-size: 12px;
}
</style>
