<template>
  <div class="min-h-screen flex items-center justify-center bg-background">
    <div class="text-center">
      <LoadingSpinner v-if="isProcessing" />
      <div v-else-if="error" class="space-y-4">
        <h2 class="text-2xl font-bold text-destructive">Authentication Failed</h2>
        <p class="text-muted-foreground">{{ error }}</p>
        <BaseButton @click="goToLogin">Back to Login</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const isProcessing = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const success = await authStore.handleOAuthCallback()
    
    if (success) {
      // Redirect to dashboard
      router.push({ name: 'Dashboard' })
    } else {
      error.value = authStore.error || 'Authentication failed'
      isProcessing.value = false
    }
  } catch (err) {
    error.value = err.message || 'Failed to complete authentication'
    isProcessing.value = false
  }
})

const goToLogin = () => {
  router.push({ name: 'Login' })
}
</script>
