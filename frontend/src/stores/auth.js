import { defineStore } from 'pinia'
import authenticationService from '@/services/api/authenticationService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    userEmail: (state) => state.user?.email || '',
    userFullName: (state) => state.user?.full_name || '',
    userAvatar: (state) => state.user?.avatar_url || null
  },

  actions: {
    /**
     * Initialize authentication on app load
     */
    async initializeAuthentication() {
      // Check if user is authenticated
      if (!authenticationService.isAuthenticated()) {
        return
      }

      // Try to load cached user profile
      const cachedUser = authenticationService.getUserProfile()
      if (cachedUser) {
        this.user = cachedUser
      }

      // Fetch fresh user profile from API
      try {
        await this.fetchCurrentUser()
      } catch (error) {
        // Token might be expired, clear auth
        this.handleLogout()
      }
    },

    /**
     * Initiate Google OAuth login
     */
    async initiateGoogleLogin() {
      this.isLoading = true
      this.error = null

      try {
        const authUrl = await authenticationService.getGoogleAuthorizationUrl()
        // Redirect to Google OAuth
        window.location.href = authUrl
      } catch (error) {
        this.error = error.detail || 'Failed to initiate Google login'
        this.isLoading = false
      }
    },

    /**
     * Handle OAuth callback
     * Extract token from URL and fetch user profile
     */
    async handleOAuthCallback() {
      const urlParams = new URLSearchParams(window.location.search)
      const token = urlParams.get('token')
      const userId = urlParams.get('user_id')

      if (!token) {
        this.error = 'No authentication token received'
        return false
      }

      // Store token
      authenticationService.storeAccessToken(token)

      // Fetch user profile
      try {
        await this.fetchCurrentUser()
        
        // Clear URL parameters
        window.history.replaceState({}, document.title, window.location.pathname)
        
        return true
      } catch (error) {
        this.error = error.detail || 'Failed to fetch user profile'
        authenticationService.clearTokens()
        return false
      }
    },

    /**
     * Fetch current user profile from API
     */
    async fetchCurrentUser() {
      this.isLoading = true
      this.error = null

      try {
        const userProfile = await authenticationService.getCurrentUserProfile()
        this.user = userProfile
        
        // Cache user profile
        authenticationService.storeUserProfile(userProfile)
        
        this.isLoading = false
      } catch (error) {
        this.error = error.detail || 'Failed to fetch user profile'
        this.isLoading = false
        throw error
      }
    },

    /**
     * Refresh access token
     */
    async refreshAccessToken() {
      try {
        await authenticationService.refreshAccessToken()
      } catch (error) {
        this.handleLogout()
        throw error
      }
    },

    /**
     * Logout user
     */
    async handleLogout() {
      this.isLoading = true

      try {
        await authenticationService.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.error = null
        this.isLoading = false
      }
    }
  }
})


