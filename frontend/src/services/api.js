import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add interceptors if needed (e.g., for auth tokens)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  // Files
  getFiles: () => api.get('/files'),
  uploadFile: (formData) => api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteFile: (id) => api.delete(`/files/${id}`),
  
  // Chat
  sendMessage: (message, contextId) => api.post('/chat', { message, contextId }),
  getChatHistory: (contextId) => api.get(`/chat/history/${contextId}`),
  
  // Auth
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data)
}
