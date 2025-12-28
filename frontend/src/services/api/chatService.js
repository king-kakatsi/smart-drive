/**
 * Chat Service
 * Handles AI chat operations and WebSocket connections
 */
import apiClient from './apiClient'
import environment from '@/config/environment'

class ChatService {
  constructor() {
    this.websocket = null
    this.messageHandlers = []
  }

  /**
   * Connect to WebSocket for real-time chat
   */
  connectWebSocket(onMessage, onError) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('No access token found')
    }

    const wsUrl = `${environment.apiWebSocketUrl}/api/v1/chat/ws/chat`
    this.websocket = new WebSocket(wsUrl)

    this.websocket.onopen = () => {
      console.log('WebSocket connected')
    }

    this.websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (onMessage) {
          onMessage(data)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) {
        onError(error)
      }
    }

    this.websocket.onclose = () => {
      console.log('WebSocket disconnected')
    }

    return this.websocket
  }

  /**
   * Send message via WebSocket
   */
  sendMessage(message, sessionId = null, fileIds = []) {
    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected')
    }

    const payload = {
      message,
      session_id: sessionId,
      file_ids: fileIds
    }

    this.websocket.send(JSON.stringify(payload))
  }

  /**
   * Disconnect WebSocket
   */
  disconnectWebSocket() {
    if (this.websocket) {
      this.websocket.close()
      this.websocket = null
    }
  }

  /**
   * Send chat message via REST API (non-streaming)
   */
  async sendChatMessage(message, sessionId = null, fileIds = []) {
    return await apiClient.post('/api/v1/chat', {
      message,
      session_id: sessionId,
      file_ids: fileIds
    })
  }

  /**
   * Get chat history for a session
   */
  async getChatHistory(sessionId) {
    return await apiClient.get(`/api/v1/chat/history/${sessionId}`)
  }
}

// Export singleton instance
export default new ChatService()
