<template>
  <MainLayout>
    <router-view />
  </MainLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import MainLayout from '@/components/layout/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useFilesStore } from '@/stores/files'

const authStore = useAuthStore()
const filesStore = useFilesStore()

onMounted(async () => {
  // Initialize the files store (load persisted data)
  filesStore.initializeStore()

  // Load files data if user is authenticated
  if (authStore.isAuthenticated && !filesStore.isDataLoaded) {
    filesStore.isLoading = true
    try {
      await Promise.all([
        filesStore.fetchAllFiles(),
        filesStore.fetchDriveFiles(100)
      ])
      filesStore.isDataLoaded = true
    } catch (error) {
      console.error('Failed to load initial data:', error)
    } finally {
      filesStore.isLoading = false
    }
  }
})
</script>

<style scoped>
/* Basic styles */
</style>
