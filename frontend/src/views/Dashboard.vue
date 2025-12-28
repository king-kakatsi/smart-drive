<template>
  <div class="space-y-8">
    <!-- Welcome Section -->
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            Welcome to Smart-Drive
          </h1>
          <p class="text-gray-600 mt-2">
            Your AI-powered document and video analysis platform
          </p>
        </div>
        <div class="text-right">
          <div class="text-sm text-gray-500">Total Files</div>
          <div class="text-2xl font-bold text-blue-600">{{ stats.totalFiles }}</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/files')">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z"></path>
            </svg>
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">File Manager</h3>
            <p class="text-sm text-gray-600">Upload and organize your files</p>
          </div>
        </div>
      </div>

      <div class="card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/chat')">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">AI Assistant</h3>
            <p class="text-sm text-gray-600">Chat with your documents</p>
          </div>
        </div>
      </div>

      <div class="card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/settings')">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">Settings</h3>
            <p class="text-sm text-gray-600">Configure Google Drive</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Files -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900">Recent Files</h2>
        <router-link to="/files" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
          View all ->
        </router-link>
      </div>

      <div v-if="recentFiles.length === 0" class="text-center py-8 text-gray-500">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p>No files uploaded yet</p>
        <router-link to="/files" class="text-blue-600 hover:text-blue-800 mt-2 inline-block">
          Upload your first file ->
        </router-link>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="file in recentFiles"
          :key="file.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
              <span class="text-xs font-medium text-blue-600">{{ getFileIcon(file.file_type) }}</span>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ file.original_filename }}</p>
              <p class="text-xs text-gray-500">
                {{ formatFileSize(file.file_size) }} - {{ formatDate(file.created_at) }}
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span
              :class="getStatusBadgeClass(file.processed)"
              class="px-2 py-1 rounded-full text-xs font-medium"
            >
              {{ file.processed ? 'Processed' : 'Processing' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({
  totalFiles: 0,
  totalSize: 0
})

const recentFiles = ref([])

onMounted(async () => {
  await loadStats()
  await loadRecentFiles()
})

const loadStats = async () => {
  try {
    const response = await axios.get('/api/v1/files/')
    stats.value.totalFiles = response.data.length
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadRecentFiles = async () => {
  try {
    const response = await axios.get('/api/v1/files/?limit=5')
    recentFiles.value = response.data
  } catch (error) {
    console.error('Failed to load recent files:', error)
  }
}

const getFileIcon = (fileType) => {
  const icons = {
    document: 'DOC',
    video: 'VID',
    audio: 'AUD',
    image: 'IMG'
  }
  return icons[fileType] || 'FILE'
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const getStatusBadgeClass = (processed) => {
  return processed
    ? 'bg-green-100 text-green-800'
    : 'bg-yellow-100 text-yellow-800'
}
</script>


