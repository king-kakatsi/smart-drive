/**
 * Authentication Service
 * Handles Google OAuth and JWT token management
 */
import apiClient from './apiClient'

class AuthenticationService {
  /**
   * Get Google OAuth authorization URL
   */
  async getGoogleAuthorizationUrl() {
    const response = await apiClient.get('/api/v1/auth/google/login')
    return response.auth_url
  }

  /**
   * Handle Google OAuth callback
   * Exchange authorization code for JWT tokens
   */
  async handleGoogleOAuthCallback(code) {
    // The backend handles this via GET redirect, so we don't call it from frontend
    // Tokens are returned via redirect URL parameters
    // This method is kept for potential future use
    throw new Error('OAuth callback is handled by backend redirect')
  }

  /**
   * Get current user profile
   */
  async getCurrentUserProfile() {
    return await apiClient.get('/api/v1/auth/me')
  }

  /**
   * Refresh access token
   */
  async refreshAccessToken() {
    const response = await apiClient.post('/api/v1/auth/refresh')
    if (response.access_token) {
      this.storeAccessToken(response.access_token)
    }
    return response.access_token
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      await apiClient.post('/api/v1/auth/logout')
    } finally {
      this.clearTokens()
    }
  }

  /**
   * Store access token in localStorage
   */
  storeAccessToken(token) {
    localStorage.setItem('access_token', token)
  }

  /**
   * Get access token from localStorage
   */
  getAccessToken() {
    return localStorage.getItem('access_token')
  }

  /**
   * Clear all tokens from localStorage
   */
  clearTokens() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_profile')
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getAccessToken()
  }

  /**
   * Store user profile in localStorage
   */
  storeUserProfile(user) {
    localStorage.setItem('user_profile', JSON.stringify(user))
  }

  /**
   * Get user profile from localStorage
   */
  getUserProfile() {
    const profile = localStorage.getItem('user_profile')
    return profile ? JSON.parse(profile) : null
  }
}

// Export singleton instance
export default new AuthenticationService()
