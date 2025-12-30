<template>
  <div class="min-h-screen flex items-center justify-center bg-background">
    <div class="max-w-md w-full space-y-8 p-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-foreground mb-2">Smart-Drive</h1>
        <p class="text-muted-foreground">Sign in to access your files and AI assistant</p>
      </div>

      <div v-if="error" class="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded">
        {{ error }}
      </div>

      <BaseButton 
        @click="handleGoogleLogin"
        :disabled="isLoading"
        class="w-full"
        size="lg"
      >
        <span v-if="!isLoading">Sign in with Google</span>
        <span v-else>Redirecting...</span>
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/common/BaseButton.vue'

const authStore = useAuthStore()
const isLoading = ref(false)
const error = ref(null)

const handleGoogleLogin = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    await authStore.initiateGoogleLogin()
  } catch (err) {
    error.value = err.message || 'Failed to initiate Google login'
    isLoading.value = false
  }
}
</script>
