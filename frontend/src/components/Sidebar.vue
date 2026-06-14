<template>
  <div class="sidebar">
    <button class="new-btn" @click="$emit('new-chat')">+ 新对话</button>
    <div class="session-list">
      <div
        v-for="s in sessions"
        :key="s.id"
        :class="['session-item', { active: s.id === currentSessionId }]"
        @click="$emit('select-session', s.id)"
      >
        <span class="title">{{ s.title || '新对话' }}</span>
        <span class="time">{{ formatTime(s.updated_at) }}</span>
        <button
          class="delete-btn"
          title="删除对话"
          @click.stop="$emit('delete-session', s.id)"
        >&times;</button>
      </div>
      <div v-if="sessions.length === 0" class="empty">暂无对话</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sessions: { type: Array, default: () => [] },
  currentSessionId: { type: Number, default: null },
})
defineEmits(['select-session', 'new-chat', 'delete-session'])

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000 && d.getDate() === now.getDate()) return '今天'
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  background: #202123;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.new-btn {
  margin: 12px;
  padding: 10px;
  background: transparent;
  color: #fff;
  border: 1px solid #4b5563;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}
.new-btn:hover {
  background: #2d2f32;
}
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}
.session-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 2px;
  transition: background 0.15s;
  position: relative;
}
.session-item:hover {
  background: #2d2f32;
}
.session-item.active {
  background: #343541;
}
.session-item .delete-btn {
  display: none;
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #8e8ea0;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}
.session-item:hover .delete-btn {
  display: block;
}
.session-item .delete-btn:hover {
  color: #ef4444;
}
.title {
  color: #ececec;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.time {
  color: #8e8ea0;
  font-size: 12px;
}
.empty {
  color: #8e8ea0;
  font-size: 13px;
  padding: 16px;
  text-align: center;
}
</style>
