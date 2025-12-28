import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [
      {
        id: 1,
        role: 'assistant',
        content: "Hello! I'm your AI assistant. I can help you analyze your documents and videos. What would you like to know?",
        timestamp: '10:00 AM'
      }
    ],
    isTyping: false,
    currentContext: null
  }),
  
  actions: {
    addMessage(message) {
      this.messages.push({
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        ...message
      })
    },
    setContext(file) {
      this.currentContext = file
    },
    clearHistory() {
      this.messages = [this.messages[0]]
    },
    async sendMessage(content) {
      this.addMessage({ role: 'user', content })
      
      this.isTyping = true
      
      // Simulate API call
      setTimeout(() => {
        this.isTyping = false
        this.addMessage({
          role: 'assistant',
          content: "I've analyzed your request. Based on the documents provided, here is the information you requested..."
        })
      }, 1500)
    }
  }
})
