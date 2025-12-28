import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.token
  },

  actions: {
    async initializeAuth() {
      // Check for stored token
      const token = localStorage.getItem('auth_token')
      if (token) {
        this.token = token
        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

        try {
          // Verify token with backend
          const response = await axios.get(`${API_BASE}/auth/me`)
          this.user = response.data
          this.isAuthenticated = true
        } catch (error) {
          // Token invalid, clear it
          this.logout()
        }
      }
    },

    async loginWithGoogle() {
      // Redirect to Google OAuth
      window.location.href = `${API_BASE}/auth/google/login`
    },

    handleAuthCallback(token, userData) {
      this.token = token
      this.user = userData
      this.isAuthenticated = true

      // Store token
      localStorage.setItem('auth_token', token)

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false

      // Clear stored token
      localStorage.removeItem('auth_token')

      // Clear axios header
      delete axios.defaults.headers.common['Authorization']
    },

    async refreshToken() {
      try {
        const response = await axios.post(`${API_BASE}/auth/refresh`)
        const newToken = response.data.access_token

        this.token = newToken
        localStorage.setItem('auth_token', newToken)
        axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`

        return newToken
      } catch (error) {
        this.logout()
        throw error
      }
    }
  }
})


