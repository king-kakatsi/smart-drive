<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useFilesStore } from '@/stores/files'
import FileExplorer from '@/components/files/FileExplorer.vue'
import UploadModal from '@/components/files/UploadModal.vue'
import FilePreviewModal from '@/components/files/FilePreviewModal.vue'
import fileService from '@/services/api/fileService'
import driveService from '@/services/api/driveService'

const props = defineProps({
  initialFolderPath: {
    type: String,
    default: '/'
  }
})

const route = useRoute()
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
    let blob
    let filename = file.name || 'download'

    // Get file blob using authenticated request
    if (file.webViewLink) {
      // Google Drive file
      blob = await driveService.downloadDriveFile(file.id)
    } else if (file.id && !isNaN(file.id)) {
      // Local file
      blob = await fileService.downloadFile(file.id)
    } else {
      console.error('Cannot download file: invalid file data', file)
      return
    }

    // Create download link from blob
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'

    document.body.appendChild(link)
    link.click()

    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to download file:', error)
    throw error
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

// Folder navigation state
const currentFiles = computed(() => filesStore.folderContents)
const currentPath = computed(() => filesStore.currentFolderPath)
const folderHistory = computed(() => filesStore.folderHistory)
const isNavigating = computed(() => filesStore.isNavigating)

// Computed path segments for breadcrumbs
const pathSegments = computed(() =>
  currentPath.value.split('/').filter(Boolean)
)

const getPathUpTo = (index) => {
  return '/' + pathSegments.value.slice(0, index + 1).join('/')
}

// Handle folder clicks
const handleOpenFolder = async (folder) => {
  try {
    const newPath = currentPath.value === '/'
      ? `/${folder.name}`
      : `${currentPath.value}/${folder.name}`

    await filesStore.navigateToFolder(newPath, folder.id)
  } catch (error) {
    console.error('Failed to navigate to folder:', error)
  }
}

// Handle breadcrumb clicks
const handleBreadcrumbClick = async (targetPath) => {
  try {
    await filesStore.navigateToFolder(targetPath)
  } catch (error) {
    console.error('Failed to navigate via breadcrumb:', error)
  }
}

// Handle browser navigation
watch(() => route.params.folderPath, (newPath) => {
  if (newPath) {
    const path = '/' + newPath.join('/')
    if (path !== currentPath.value && !isNavigating.value) {
      filesStore.navigateToFolder(path)
    }
  }
})

// Initialize folder contents
onMounted(async () => {
  try {
    if (props.initialFolderPath && props.initialFolderPath !== '/') {
      await filesStore.navigateToFolder(props.initialFolderPath)
    } else {
      await filesStore.fetchFolderContents('/')
    }
  } catch (error) {
    console.error('Failed to initialize folder contents:', error)
  }
})
</script>

<template>
  <div class="h-full">
    <!-- Loading Overlay -->
    <div v-if="isNavigating" class="absolute inset-0 bg-background/80 flex items-center justify-center z-50">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>

    <!-- Breadcrumb Navigation -->
    <div class="mt-4 mb-4 flex items-center justify-between px-4 lg:px-8">
      <div class="flex items-center gap-2 text-sm">
        <button
          @click="handleBreadcrumbClick('/')"
          class="hover:text-primary transition-colors"
          :class="{ 'text-primary font-medium': currentPath === '/' }"
        >
          Home
        </button>

        <template v-for="(segment, index) in pathSegments" :key="segment">
          <span class="text-muted-foreground">/</span>
          <button
            @click="handleBreadcrumbClick(getPathUpTo(index))"
            class="hover:text-primary transition-colors"
            :class="{
              'text-primary font-medium': getPathUpTo(index) === currentPath
            }"
          >
            {{ segment }}
          </button>
        </template>
      </div>

      <!-- Navigation Buttons -->
      <div class="flex items-center gap-2">
        <button
          v-if="folderHistory.length > 1"
          @click="filesStore.navigateUp()"
          class="px-3 py-1.5 text-sm bg-muted hover:bg-muted/80 rounded-md transition-colors"
        >
          Back
        </button>
      </div>
    </div>

    <!-- Folder Contents -->
    <FileExplorer
      :files="currentFiles"
      :title="pathSegments.length ? pathSegments[pathSegments.length - 1] : 'All Files'"
      empty-message="This folder is empty"
      empty-description="Upload files or create subfolders to get started."
      @open-chat="handleOpenChat"
      @show-upload="isUploadOpen = true"
      @preview-file="handlePreviewFile"
      @open-folder="handleOpenFolder"
      @open-file="handleOpenFile"
    />

    <!-- Modals -->
    <UploadModal :is-open="isUploadOpen" @close="isUploadOpen = false" />
    <FilePreviewModal :is-open="isPreviewOpen" :file="selectedFile" @close="isPreviewOpen = false"
      @open-chat="handleOpenChat" @download="handleDownload" @delete="handleDelete" @share="handleShare" />
  </div>
</template>
