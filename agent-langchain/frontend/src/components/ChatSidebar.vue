<script setup>
import { useAppStore } from '../stores/app'

defineProps({ open: Boolean })
const emit = defineEmits(['new-chat', 'close'])
const store = useAppStore()

function formatDate(value) {
  const date = new Date(value)
  const today = new Date()
  if (date.toDateString() === today.toDateString()) {
    return `今天 · ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
  }
  return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
}
</script>

<template>
  <div v-if="open" class="sidebar-scrim" @click="emit('close')"></div>
  <aside class="sidebar" :class="{ 'sidebar-open': open }">
    <div class="brand-row">
      <span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4.5 12c2.1-5.1 7-7.2 12.8-3.1 1 .7 1.7 1.8 2.2 3.1-2.1 5.1-7 7.2-12.8 3.1-1-.7-1.7-1.8-2.2-3.1Z"/><circle cx="12" cy="12" r="2.1"/></svg></span>
      <span class="brand-name">知伴 AI</span>
      <button class="icon-button sidebar-close" aria-label="关闭侧栏" @click="emit('close')"><svg viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18"/></svg></button>
    </div>

    <button class="new-chat-button" @click="emit('new-chat')">
      <svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg><span>新建对话</span>
    </button>

    <div class="conversation-heading">最近对话</div>
    <nav class="conversation-list" aria-label="最近对话">
      <button
        v-for="conversation in store.conversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ selected: conversation.id === store.activeConversationId }"
        @click="store.selectConversation(conversation.id); emit('close')"
      >
        <span class="conversation-title">{{ conversation.title }}</span>
        <span class="conversation-date">{{ formatDate(conversation.updatedAt) }}</span>
      </button>
      <p v-if="store.conversations.length === 0" class="empty-history">新对话会显示在这里</p>
    </nav>

    <div class="profile-area">
      <div class="profile-avatar">林</div>
      <div class="profile-copy"><strong>林同学</strong><span>个人工作区</span></div>
      <button class="icon-button profile-menu" aria-label="个人菜单"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></svg></button>
    </div>
  </aside>
</template>
