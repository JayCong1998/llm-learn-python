<script setup>
import DOMPurify from 'dompurify'
import { marked } from 'marked'

const props = defineProps({ message: { type: Object, required: true } })
const emit = defineEmits(['retry'])

marked.setOptions({ breaks: true, gfm: true })

function safeMarkdown(content) {
  return DOMPurify.sanitize(marked.parse(content || ''))
}

async function copyMessage() {
  await navigator.clipboard.writeText(props.message.content || '')
}
</script>

<template>
  <article class="message-row" :class="`message-${message.role}`">
    <template v-if="message.role === 'user'">
      <div class="user-bubble"><div class="message-markdown" v-html="safeMarkdown(message.content)"></div></div>
      <div class="user-avatar">我</div>
    </template>

    <template v-else>
      <div class="assistant-avatar"><svg viewBox="0 0 24 24"><path d="M4.5 12c2.1-5.1 7-7.2 12.8-3.1 1 .7 1.7 1.8 2.2 3.1-2.1 5.1-7 7.2-12.8 3.1-1-.7-1.7-1.8-2.2-3.1Z"/><circle cx="12" cy="12" r="2.1"/></svg></div>
      <div class="assistant-body">
        <div class="assistant-byline"><strong>知伴 AI</strong><span>· Qwen</span></div>
        <div v-if="message.tools?.length" class="tool-list">
          <div v-for="(tool, index) in message.tools" :key="tool.tool_call_id || index" class="tool-event" :class="`tool-${tool.status}`">
            <span class="tool-status-dot"></span>
            <span>{{ tool.status === 'running' ? '正在调用' : tool.status === 'failed' ? '调用失败' : '已完成' }}</span>
            <strong>{{ tool.tool_name || '工具' }}</strong>
            <span v-if="tool.status === 'running'" class="tool-spinner"></span>
          </div>
        </div>
        <div v-if="message.content" class="message-markdown" v-html="safeMarkdown(message.content)"></div>
        <div v-else-if="message.status === 'streaming'" class="typing-indicator" aria-label="正在生成"><i></i><i></i><i></i></div>
        <div v-if="message.status === 'error'" class="message-error">{{ message.error || '回复生成失败，请重试。' }}</div>
        <div v-if="message.status === 'stopped'" class="message-stopped">已停止生成</div>
        <div v-if="message.content || message.status === 'error'" class="message-actions">
          <button v-if="message.content" class="action-button" aria-label="复制回答" title="复制回答" @click="copyMessage"><svg viewBox="0 0 24 24"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/></svg></button>
          <button v-if="message.status === 'error'" class="action-button retry-button" @click="emit('retry')">重新生成</button>
        </div>
      </div>
    </template>
  </article>
</template>
