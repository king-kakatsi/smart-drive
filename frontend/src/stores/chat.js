import { defineStore } from 'pinia'
import chatService from '@/services/api/chatService'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    sessionId: null,
    isTyping: false,
    isConnected: false,
    error: null,
    currentContext: null,
    selectedFileIds: []
  }),
  
  getters: {
    hasMessages: (state) => state.messages.length > 0,
    lastMessage: (state) => state.messages[state.messages.length - 1]
  },

  actions: {
    /**
     * Initialize WebSocket connection
     */
    initializeWebSocket() {
      try {
        chatService.connectWebSocket(
          this.handleWebSocketMessage,
          this.handleWebSocketError
        )
        this.isConnected = true
        this.error = null
      } catch (error) {
        this.error = error.message || 'Failed to connect to chat'
        this.isConnected = false
      }
    },

    /**
     * Handle incoming WebSocket messages
     */
    handleWebSocketMessage(data) {
      if (data.type === 'start') {
        // AI started responding
        this.isTyping = true
        this.addMessage({
          role: 'assistant',
          content: '',
          sources: []
        })
      } else if (data.type === 'stream') {
        // Streaming content
        const index = this.messages.length - 1
        if (index >= 0 && this.messages[index].role === 'assistant') {
          // Re-assign to ensure reactivity in all Vue versions
          const updatedMsg = { ...this.messages[index] }
          updatedMsg.content += (data.content || '')
          this.messages[index] = updatedMsg
        }
      } else if (data.type === 'source') {
        // Source citation
        const lastMessage = this.messages[this.messages.length - 1]
        if (lastMessage && lastMessage.role === 'assistant') {
          if (!lastMessage.sources) {
            lastMessage.sources = []
          }
          lastMessage.sources.push(data.source)
        }
      } else if (data.type === 'end') {
        // AI finished responding
        this.isTyping = false
        if (data.session_id) {
          this.sessionId = data.session_id
        }
      } else if (data.type === 'error') {
        // Error occurred
        this.isTyping = false
        this.error = data.message
      }
    },

    /**
     * Handle WebSocket errors
     */
    handleWebSocketError(error) {
      this.error = 'WebSocket connection error'
      this.isConnected = false
      this.isTyping = false
    },

    /**
     * Send message via WebSocket
     */
    async sendMessage(content) {
      if (!content.trim()) return

      // Add user message
      this.addMessage({
        role: 'user',
        content: content.trim()
      })

      this.error = null

      try {
        if (!this.isConnected) {
          this.initializeWebSocket()
        }

        chatService.sendMessage(
          content.trim(),
          this.sessionId,
          this.selectedFileIds
        )
      } catch (error) {
        this.error = error.message || 'Failed to send message'
        this.isTyping = false
      }
    },

    /**
     * Add message to chat history
     */
    addMessage(message) {
      this.messages.push({
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        ...message
      })
    },

    /**
     * Load chat history for a session
     */
    async loadChatHistory(sessionId) {
      this.error = null

      try {
        const history = await chatService.getChatHistory(sessionId)
        this.messages = history.messages || []
        this.sessionId = sessionId
      } catch (error) {
        this.error = error.detail || 'Failed to load chat history'
      }
    },

    /**
     * Set context files for chat
     */
    setContextFiles(fileIds) {
      this.selectedFileIds = fileIds
    },

    /**
     * Start chat with a specific file context
     */
    startChatWithFile(file) {
      this.clearHistory()
      this.setContextFiles([file.id])
      this.currentContext = file
    },

    /**
     * Clear context files
     */
    clearContext() {
      this.selectedFileIds = []
      this.currentContext = null
    },

    /**
     * Clear chat history
     */
    clearHistory() {
      this.messages = []
      this.sessionId = null
      this.selectedFileIds = []
      this.currentContext = null
    },

    /**
     * Disconnect WebSocket
     */
    disconnect() {
      chatService.disconnectWebSocket()
      this.isConnected = false
    }
  }
})
