/**
 * Environment configuration
 * Centralized access to environment variables
 */

const environment = {
  // API Configuration
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiWebSocketUrl: import.meta.env.VITE_API_WEBSOCKET_URL || 'ws://localhost:8000',
  
  // Google OAuth
  googleClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
  
  // Application
  appName: import.meta.env.VITE_APP_NAME || 'Smart-Drive',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // Environment
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
}

export default environment
