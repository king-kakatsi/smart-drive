/**
 * Base API Client
 * Handles all HTTP requests with automatic token management
 */
import environment from '@/config/environment'

class ApiClient {
  constructor() {
    this.baseUrl = environment.apiBaseUrl
  }

  /**
   * Get authorization header with JWT token
   */
  getAuthorizationHeader() {
    const token = localStorage.getItem('access_token')
    return token ? { 'Authorization': `Bearer ${token}` } : {}
  }

  /**
   * Handle API response
   */
  async handleResponse(response) {
    if (!response.ok) {
      const error = new Error(`HTTP ${response.status}`)
      error.status = response.status
      error.statusText = response.statusText
      
      try {
        const errorData = await response.json()
        error.detail = errorData.detail || errorData.message || response.statusText
      } catch {
        error.detail = response.statusText
      }
      
      throw error
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    }
    
    return await response.text()
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthorizationHeader(),
      ...options.headers
    }

    const response = await fetch(url, {
      method: 'GET',
      headers,
      ...options
    })

    return this.handleResponse(response)
  }

  /**
   * POST request
   */
  async post(endpoint, data = null, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthorizationHeader(),
      ...options.headers
    }

    const config = {
      method: 'POST',
      headers,
      ...options
    }

    if (data) {
      config.body = JSON.stringify(data)
    }

    const response = await fetch(url, config)
    return this.handleResponse(response)
  }

  /**
   * PUT request
   */
  async put(endpoint, data = null, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthorizationHeader(),
      ...options.headers
    }

    const config = {
      method: 'PUT',
      headers,
      ...options
    }

    if (data) {
      config.body = JSON.stringify(data)
    }

    const response = await fetch(url, config)
    return this.handleResponse(response)
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthorizationHeader(),
      ...options.headers
    }

    const response = await fetch(url, {
      method: 'DELETE',
      headers,
      ...options
    })

    return this.handleResponse(response)
  }

  /**
   * Upload file with FormData
   */
  async uploadFile(endpoint, formData, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const headers = {
      ...this.getAuthorizationHeader(),
      ...options.headers
    }
    // Do not set Content-Type for FormData, browser will set it with boundary

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
      ...options
    })

    return this.handleResponse(response)
  }
}

// Export singleton instance
export default new ApiClient()
