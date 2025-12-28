<template>
  <header class="bg-white shadow-sm border-b">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-sm">SD</span>
          </div>
          <span class="text-xl font-bold text-gray-900">Smart-Drive</span>
        </router-link>

        <!-- Navigation -->
        <nav class="hidden md:flex space-x-8">
          <router-link
            to="/"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600': $route.path === '/' }"
          >
            Dashboard
          </router-link>
          <router-link
            to="/files"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600': $route.path === '/files' }"
          >
            Files
          </router-link>
          <router-link
            to="/chat"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600': $route.path === '/chat' }"
          >
            AI Chat
          </router-link>
          <router-link
            to="/settings"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600': $route.path === '/settings' }"
          >
            Settings
          </router-link>
        </nav>

        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <div v-if="user" class="flex items-center space-x-2">
            <span class="text-sm text-gray-700">{{ user.full_name }}</span>
            <button
              @click="logout"
              class="text-gray-600 hover:text-gray-900 px-3 py-1 rounded text-sm"
            >
              Logout
            </button>
          </div>
          <div v-else>
            <button
              @click="login"
              class="btn-primary text-sm"
            >
              Login with Google
            </button>
          </div>
        </div>

        <!-- Mobile menu button -->
        <button
          @click="toggleMobileMenu"
          class="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="showMobileMenu" class="md:hidden border-t py-4">
        <nav class="flex flex-col space-y-2">
          <router-link
            to="/"
            @click="closeMobileMenu"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
          >
            Dashboard
          </router-link>
          <router-link
            to="/files"
            @click="closeMobileMenu"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
          >
            Files
          </router-link>
          <router-link
            to="/chat"
            @click="closeMobileMenu"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
          >
            AI Chat
          </router-link>
          <router-link
            to="/settings"
            @click="closeMobileMenu"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
          >
            Settings
          </router-link>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const showMobileMenu = ref(false)

const user = computed(() => authStore.user)

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const closeMobileMenu = () => {
  showMobileMenu.value = false
}

const login = () => {
  // Redirect to Google OAuth
  window.location.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/google/login`
}

const logout = () => {
  authStore.logout()
}
</script>


