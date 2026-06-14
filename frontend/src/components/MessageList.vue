<template>
  <div class="message-list" ref="listEl">
    <div class="messages">
      <MessageBubble
        v-for="(msg, i) in messages"
        :key="i"
        :role="msg.role"
        :content="msg.content"
      />
      <div v-if="streaming" class="cursor">▊</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  streaming: { type: Boolean, default: false },
})

const listEl = ref(null)

function scrollBottom() {
  nextTick(() => {
    if (listEl.value) {
      listEl.value.scrollTop = listEl.value.scrollHeight
    }
  })
}

watch(() => props.messages.length, scrollBottom)
watch(() => props.streaming, scrollBottom)
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}
.messages {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px;
}
.cursor {
  color: #4f46e5;
  font-size: 18px;
  padding: 0 0 0 56px;
  animation: blink 1s steps(1) infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}
</style>
