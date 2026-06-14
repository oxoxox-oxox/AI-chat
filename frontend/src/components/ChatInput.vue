<template>
  <div class="chat-input">
    <textarea
      ref="inputEl"
      v-model="text"
      placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
      rows="1"
      :disabled="disabled"
      @keydown="onKeydown"
      @input="autoResize"
    />
    <button :disabled="disabled || !text.trim()" @click="send">
      {{ disabled ? '思考中...' : '发送' }}
    </button>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['send'])

const text = ref('')
const inputEl = ref(null)

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

function send() {
  const msg = text.value.trim()
  if (!msg || props.disabled) return
  emit('send', msg)
  text.value = ''
  nextTick(() => {
    if (inputEl.value) {
      inputEl.value.style.height = 'auto'
    }
  })
}

function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}
</script>

<style scoped>
.chat-input {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  background: #fff;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}
textarea {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  outline: none;
  line-height: 1.5;
  max-height: 160px;
}
textarea:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15);
}
button {
  padding: 10px 20px;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}
button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
button:not(:disabled):hover {
  background: #4338ca;
}
</style>
