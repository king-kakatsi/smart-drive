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
import { Home, ChevronRight, ArrowLeft } from 'lucide-vue-next'
import { cn } from '@/utils/cn'

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
      // For local files, use the share API endpoint
      const response = await fetch(`/api/v1/files/${file.id}/share`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        await navigator.clipboard.writeText(data.share_url)
        alert(`Share link copied to clipboard!\nExpires in ${data.expires_in}`)
      } else {
        throw new Error('Failed to generate share link')
      }
    }
  } catch (error) {
    console.error('Failed to share file:', error)
    alert('Failed to generate share link. Please try again.')
  }
}

const handleOpenInTab = async (file) => {
  try {
    // Determine if local or Drive file and open appropriate preview URL
    if (file.webViewLink) {
      // Google Drive file - open web view link in new tab
      window.open(file.webViewLink, '_blank')
    } else if (file.id && !isNaN(file.id)) {
      // Local file - use preview endpoint
      const previewUrl = `/api/v1/files/${file.id}/preview`
      window.open(previewUrl, '_blank')
    } else {
      console.error('Cannot open file in tab: invalid file data', file)
      alert('Cannot open file: invalid file data')
    }
  } catch (error) {
    console.error('Failed to open file in tab:', error)
    alert('Failed to open file. Please try again.')
  }
}

// Folder navigation state - switch to global filtered files when searching
const currentFiles = computed(() => {
  if (filesStore.searchQuery) {
    return filesStore.filteredFiles
  }
  return filesStore.folderContents
})
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
    const folderName = folder.name || folder.original_filename || folder.filename || 'Unnamed Folder'
    const newPath = currentPath.value === '/'
      ? `/${folderName}`
      : `${currentPath.value}/${folderName}`

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

    <!-- Breadcrumb & Navigation Bar -->
    <div
      class="sticky top-0 z-30 backdrop-blur-md bg-white/40 dark:bg-slate-900/40 border-b border-white/10 px-4 lg:px-8 py-3 flex items-center justify-between">
      <div class="flex items-center gap-1 overflow-x-auto no-scrollbar py-1">
        <!-- Root / Home Link -->
        <button @click="handleBreadcrumbClick('/')" :class="cn(
          'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all whitespace-nowrap',
          currentPath === '/'
            ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
            : 'text-muted-foreground hover:bg-muted hover:text-foreground'
        )">
          <Home class="w-3.5 h-3.5" />
          <span>Home</span>
        </button>

        <!-- Segment Links -->
        <template v-for="(segment, index) in pathSegments" :key="segment">
          <ChevronRight class="w-4 h-4 text-muted-foreground/40 shrink-0" />
          <button @click="handleBreadcrumbClick(getPathUpTo(index))" :class="cn(
            'px-3 py-1.5 rounded-full text-xs font-bold transition-all whitespace-nowrap border border-transparent',
            getPathUpTo(index) === currentPath
              ? 'bg-white dark:bg-slate-800 text-primary shadow-sm border-primary/20'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          )">
            {{ segment }}
          </button>
        </template>
      </div>

      <!-- Navigation Actions -->
      <div class="flex items-center gap-2 shrink-0 ml-4">
        <button v-if="folderHistory.length > 1" @click="filesStore.navigateUp()"
          class="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold bg-muted hover:bg-muted/80 rounded-full transition-all border border-border/50 hover:border-border">
          <ArrowLeft class="w-3.5 h-3.5" />
          <span>Back</span>
        </button>
      </div>
    </div>

    <!-- Folder Contents -->
    <FileExplorer :files="currentFiles"
      :title="filesStore.searchQuery ? 'Search Results' : (pathSegments.length ? pathSegments[pathSegments.length - 1] : 'All Files')"
      :empty-message="filesStore.searchQuery ? 'No search results found' : 'This folder is empty'"
      :empty-description="filesStore.searchQuery ? 'Try a different keyword.' : 'Upload files or create subfolders to get started.'"
      @open-chat="handleOpenChat" @show-upload="isUploadOpen = true" @preview-file="handlePreviewFile"
      @open-folder="handleOpenFolder" @open-file="handleOpenFile" @open-in-tab="handleOpenInTab"
      @toggle-star="handleToggleStar" />

    <!-- Modals -->
    <UploadModal :is-open="isUploadOpen" @close="isUploadOpen = false" />
    <FilePreviewModal :is-open="isPreviewOpen" :file="selectedFile" @close="isPreviewOpen = false"
      @open-chat="handleOpenChat" @download="handleDownload" @delete="handleDelete" @share="handleShare" />
  </div>
</template>
