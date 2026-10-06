import { defineStore } from 'pinia'

const STORAGE_KEY = 'agent-chat-conversations'

function loadConversations() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

export const useAppStore = defineStore('app', {
  state: () => ({
    conversations: loadConversations(),
    activeConversationId: null,
  }),
  getters: {
    activeConversation: (state) =>
      state.conversations.find((conversation) => conversation.id === state.activeConversationId) || null,
  },
  actions: {
    createConversation() {
      const conversation = {
        id: crypto.randomUUID(),
        title: '新建对话',
        updatedAt: new Date().toISOString(),
        messages: [],
      }
      this.conversations.unshift(conversation)
      this.activeConversationId = conversation.id
      this.persistConversations()
      return conversation
    },
    selectConversation(id) {
      this.activeConversationId = id
    },
    persistConversations() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.conversations))
    },
    touchConversation(conversation) {
      conversation.updatedAt = new Date().toISOString()
      this.conversations.sort((first, second) => new Date(second.updatedAt) - new Date(first.updatedAt))
      this.persistConversations()
    },
  },
})
