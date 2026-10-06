<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatSidebar from '../components/ChatSidebar.vue'
import { streamAgentReply } from '../api/agent'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const draft = ref('')
const isStreaming = ref(false)
const sidebarOpen = ref(false)
const messageList = ref(null)
let activeController = null

const conversation = computed(() => store.activeConversation)
const messages = computed(() => conversation.value?.messages || [])

onMounted(() => {
  if (!store.activeConversationId && store.conversations.length > 0) {
    store.selectConversation(store.conversations[0].id)
  }
})

async function scrollToLatest() {
  await nextTick()
  if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
}

function startNewChat() {
  stopGeneration()
  store.createConversation()
  sidebarOpen.value = false
  draft.value = ''
}

function makeTitle(text) {
  const singleLine = text.replace(/\s+/g, ' ').trim()
  return singleLine.length > 28 ? `${singleLine.slice(0, 28)}…` : singleLine
}

function handleAgentEvent({ name, payload }, assistantMessage, currentConversation) {
  if (!assistantMessage) return

  if (name === 'content_delta') {
    assistantMessage.content += String(payload.data ?? '')
    scrollToLatest()
  } else if (name === 'tool_call_started') {
    assistantMessage.tools.push({
      tool_call_id: payload.tool_call_id,
      tool_name: payload.tool_name,
      arguments: payload.data,
      status: 'running',
    })
    store.persistConversations()
    scrollToLatest()
  } else if (name === 'tool_result' || name === 'tool_call_failed' || name === 'tool_call_completed') {
    const tool = [...assistantMessage.tools].reverse().find((item) =>
      (payload.tool_call_id && item.tool_call_id === payload.tool_call_id) ||
      (!payload.tool_call_id && item.tool_name === payload.tool_name && item.status === 'running'),
    )
    if (tool) {
      tool.status = name === 'tool_call_failed' ? 'failed' : 'complete'
      tool.result = payload.data
    }
    store.persistConversations()
    scrollToLatest()
  } else if (name === 'error') {
    assistantMessage.error = String(payload.data || '模型暂时无法完成回复。')
    assistantMessage.status = 'error'
    store.persistConversations()
  } else if (name === 'run_completed') {
    assistantMessage.status = 'complete'
    store.touchConversation(currentConversation)
  }
}

async function sendMessage(rawText = draft.value) {
  const text = rawText.trim()
  if (!text || isStreaming.value) return

  let current = conversation.value
  if (!current) current = store.createConversation()
  if (current.messages.length === 0) current.title = makeTitle(text)
  current.messages.push({ id: crypto.randomUUID(), role: 'user', content: text, createdAt: new Date().toISOString() })
  const assistantMessage = {
    id: crypto.randomUUID(),
    role: 'assistant',
    content: '',
    tools: [],
    status: 'streaming',
    createdAt: new Date().toISOString(),
  }
  current.messages.push(assistantMessage)
  store.touchConversation(current)
  draft.value = ''
  isStreaming.value = true
  activeController = new AbortController()
  await scrollToLatest()

  try {
    await streamAgentReply(text, { signal: activeController.signal, onEvent: (event) => handleAgentEvent(event, assistantMessage, current) })
    if (assistantMessage.status === 'streaming') assistantMessage.status = 'complete'
    store.touchConversation(current)
  } catch (error) {
    if (error.name === 'AbortError') {
      if (assistantMessage.status === 'streaming') assistantMessage.status = 'stopped'
    } else if (assistantMessage.status !== 'error') {
      assistantMessage.error = error.message || '连接服务器失败，请确认 FastAPI 服务已启动。'
      assistantMessage.status = 'error'
    }
    store.persistConversations()
  } finally {
    isStreaming.value = false
    activeController = null
    await scrollToLatest()
  }
}

function stopGeneration() {
  if (!activeController) return
  activeController.abort()
}

function retryMessage(messageIndex) {
  const previousUserMessage = [...messages.value.slice(0, messageIndex)].reverse().find((message) => message.role === 'user')
  if (previousUserMessage) sendMessage(previousUserMessage.content)
}

function onComposerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    sendMessage()
  }
}

function onComposerInput(event) {
  const textarea = event.target
  textarea.style.height = 'auto'
  textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`
}
</script>

<template>
  <div class="chat-app">
    <ChatSidebar :open="sidebarOpen" @new-chat="startNewChat" @close="sidebarOpen = false" />

    <main class="chat-panel">
      <header class="chat-header">
        <button class="icon-button mobile-menu" aria-label="打开对话列表" @click="sidebarOpen = true"><svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
        <h1>{{ conversation?.title || '新建对话' }}</h1>
        <div class="model-badge"><span class="online-dot"></span><span>Qwen · 在线</span><svg viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg></div>
      </header>

      <section ref="messageList" class="message-list" aria-live="polite" @wheel.prevent>
        <div v-if="messages.length === 0" class="welcome-state">
          <div class="welcome-mark"><svg viewBox="0 0 24 24"><path d="M4.5 12c2.1-5.1 7-7.2 12.8-3.1 1 .7 1.7 1.8 2.2 3.1-2.1 5.1-7 7.2-12.8 3.1-1-.7-1.7-1.8-2.2-3.1Z"/><circle cx="12" cy="12" r="2.1"/></svg></div>
          <p class="welcome-eyebrow">你好，我是知伴 AI</p>
          <h2>今天有什么可以帮你？</h2>
          <p class="welcome-description">提问、整理思路，或让我帮你探索一个新想法。</p>
          <div class="suggestion-grid">
            <button @click="sendMessage('FastAPI 如何提供 Vue 构建后的静态页面？')"><strong>FastAPI 项目集成</strong><span>如何提供 Vue 构建后的静态页面？</span><svg viewBox="0 0 24 24"><path d="m8 16 8-8M7 8h9v9"/></svg></button>
            <button @click="sendMessage('帮我解释一下 Python 的异步编程')"><strong>学习一个概念</strong><span>帮我解释一下 Python 的异步编程</span><svg viewBox="0 0 24 24"><path d="m8 16 8-8M7 8h9v9"/></svg></button>
          </div>
        </div>

        <div v-else class="message-thread">
          <div class="date-divider"><span>本次对话</span></div>
          <ChatMessage
            v-for="(message, index) in messages"
            :key="message.id"
            :message="message"
            @retry="retryMessage(index)"
          />
        </div>
      </section>

      <footer class="composer-area">
        <form class="composer" @submit.prevent="sendMessage()">
          <label class="sr-only" for="message-input">发送给知伴 AI 的消息</label>
          <textarea
            id="message-input"
            v-model="draft"
            rows="1"
            placeholder="给知伴 AI 发送消息…"
            :disabled="isStreaming"
            @keydown="onComposerKeydown"
            @input="onComposerInput"
          ></textarea>
          <div class="composer-toolbar">
            <span class="attachment-note"><svg viewBox="0 0 24 24"><path d="M8 12.5V6a4 4 0 0 1 8 0v11a6 6 0 0 1-12 0V7M8 8v9a2 2 0 0 0 4 0V7"/></svg>支持直接输入消息</span>
            <div class="composer-submit-area"><span class="keyboard-hint">Enter 发送 · Shift + Enter 换行</span>
              <button v-if="isStreaming" class="stop-button" type="button" aria-label="停止生成" @click="stopGeneration"><span></span></button>
              <button v-else class="send-button" type="submit" aria-label="发送消息" :disabled="!draft.trim()"><svg viewBox="0 0 24 24"><path d="m21 3-7.2 18-3.6-7.2L3 10.2 21 3Z"/><path d="M10.2 13.8 15 9"/></svg></button>
            </div>
          </div>
        </form>
        <p class="disclaimer">知伴 AI 可能会出错，请核对重要信息。</p>
      </footer>
    </main>
  </div>
</template>
