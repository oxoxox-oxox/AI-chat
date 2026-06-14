<template>
  <div :class="['bubble', role]">
    <div class="avatar">{{ role === 'user' ? '👤' : '🤖' }}</div>
    <div v-if="role === 'assistant'" class="content markdown-body" v-html="rendered"></div>
    <div v-else class="content">{{ content }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import {marked} from 'marked';

const props = defineProps({
  role: {type: String, required:true},
  content: {type: String, required: true},
})

const rendered = computed(() => {
  return marked.parse(props.content)
})
</script>

<style scoped>
.bubble {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  max-width: 85%;
}
.bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}
.bubble.assistant {
  align-self: flex-start;
}
.avatar {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  background: #e5e7eb;
}
.content {
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.user .content {
  background: #4f46e5;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.assistant .content {
  background: #f3f4f6;
  color: #111827;
  border-bottom-left-radius: 4px;
}

/* Markdown 内容样式 */
.markdown-body :deep(p) { margin: 0.4em 0; }
.markdown-body :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
}
.markdown-body :deep(code) {
  background: #e5e7eb;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Fira Code', 'Consolas', monospace;
}
.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
}
.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}
.markdown-body :deep(li) { margin: 2px 0; }
.markdown-body :deep(blockquote) {
  border-left: 3px solid #d1d5db;
  padding-left: 12px;
  color: #6b7280;
  margin: 8px 0;
}
.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
}
.markdown-body :deep(th), .markdown-body :deep(td) {
  border: 1px solid #d1d5db;
  padding: 6px 10px;
}
.markdown-body :deep(th) { background: #f3f4f6; }

</style>
