import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'

export function useChat() {
  const store = useChatStore()
  const { 
    messages, 
    isTyping, 
    currentContext 
  } = storeToRefs(store)

  return {
    // State
    messages,
    isTyping,
    currentContext,

    // Actions
    sendMessage: store.sendMessage,
    setContext: store.setContext,
    clearHistory: store.clearHistory
  }
}
