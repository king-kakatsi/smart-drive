<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useFilesStore } from '@/stores/files'
import FileExplorer from '@/components/files/FileExplorer.vue'
import UploadModal from '@/components/files/UploadModal.vue'
import FilePreviewModal from '@/components/files/FilePreviewModal.vue'

const router = useRouter()
const chatStore = useChatStore()
const filesStore = useFilesStore()

const isUploadOpen = ref(false)
const isPreviewOpen = ref(false)
const selectedFile = ref(null)

const handlePreviewFile = (file) => {
  selectedFile.value = file
  isPreviewOpen.value = true
}

const handleOpenChat = (file) => {
  chatStore.startChatWithFile(file)
  router.push('/chat')
}

const handleToggleStar = async (file) => {
  try {
    await filesStore.toggleFileStar(file.id)
  } catch (error) {
    console.error('Failed to toggle star:', error)
  }
}

const handleDownload = async (file) => {
  try {
    // For Google Drive files, use the webViewLink
    if (file.webViewLink) {
      window.open(file.webViewLink, '_blank')
    } else if (file.id && !isNaN(file.id)) {
      // For local files, use the backend download endpoint
      const downloadUrl = `/api/v1/files/${file.id}/download`
      window.open(downloadUrl, '_blank')
    } else {
      console.error('Cannot download file: invalid file data', file)
    }
  } catch (error) {
    console.error('Failed to download file:', error)
  }
}

const handleOpenFile = (file) => {
  try {
    // For Google Drive files, use the webViewLink
    if (file.webViewLink) {
      window.open(file.webViewLink, '_blank')
    } else if (file.id && !isNaN(file.id)) {
      // For local files, use the backend download endpoint
      const downloadUrl = `/api/v1/files/${file.id}/download`
      window.open(downloadUrl, '_blank')
    } else {
      console.error('Cannot open file: invalid file data', file)
    }
  } catch (error) {
    console.error('Failed to open file:', error)
  }
}

const handleDelete = async (file) => {
  if (confirm(`Are you sure you want to delete "${file.name}"?`)) {
    try {
      await filesStore.deleteFile(file.id)
      // Close the preview modal after successful deletion
      isPreviewOpen.value = false
    } catch (error) {
      console.error('Failed to delete file:', error)
    }
  }
}

const handleShare = async (file) => {
  try {
    // For Google Drive files, copy the shareable link
    if (file.webViewLink) {
      await navigator.clipboard.writeText(file.webViewLink)
      alert('Share link copied to clipboard!')
    } else {
      // For local files, create a shareable link
      const shareUrl = `${window.location.origin}/shared/${file.id}`
      await navigator.clipboard.writeText(shareUrl)
      alert('Share link copied to clipboard!')
    }
  } catch (error) {
    console.error('Failed to share file:', error)
  }
}

const handleOpenFolder = (folder) => {
  // TODO: Implement folder navigation
  console.log('Open folder:', folder.name)
  // For now, just show an alert
  alert(`Folder navigation not yet implemented. Would open: ${folder.name}`)
}
</script>

<template>
  <div class="h-full">
    <FileExplorer @open-chat="handleOpenChat" @show-upload="isUploadOpen = true" @preview-file="handlePreviewFile" @toggle-star="handleToggleStar" @download="handleDownload" @delete="handleDelete" @share="handleShare" @open-folder="handleOpenFolder" @open-file="handleOpenFile" />

    <!-- Modals -->
    <UploadModal :is-open="isUploadOpen" @close="isUploadOpen = false" />
    <FilePreviewModal :is-open="isPreviewOpen" :file="selectedFile" @close="isPreviewOpen = false"
      @open-chat="handleOpenChat" @download="handleDownload" @delete="handleDelete" @share="handleShare" />
  </div>
</template>
