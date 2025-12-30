<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFilesStore } from '@/stores/files'
import { useChatStore } from '@/stores/chat'
import FileCard from '@/components/files/FileCard.vue'
import UploadModal from '@/components/files/UploadModal.vue'
import FilePreviewModal from '@/components/files/FilePreviewModal.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { Trash2, Upload } from 'lucide-vue-next'

const router = useRouter()
const chatStore = useChatStore()

const filesStore = useFilesStore()

const isUploadOpen = ref(false)
const isPreviewOpen = ref(false)
const selectedFile = ref(null)

// Filter trashed files by search query
const trashedFiles = computed(() => {
  const query = filesStore.searchQuery.toLowerCase()
  return filesStore.trashedFiles.filter(file =>
    (file.name || file.original_filename || '').toLowerCase().includes(query)
  )
})

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
</script>

<template>
  <div class="h-full">
    <div class="p-4 lg:p-8 border-b border-border">
      <div class="flex items-center gap-3">
        <Trash2 class="w-6 h-6 text-primary" />
        <h1 class="text-2xl font-bold">Trash</h1>
      </div>
      <p class="text-muted-foreground mt-2">Deleted files are kept here for 30 days</p>
    </div>

    <div class="flex-1 overflow-y-auto p-4 lg:p-8">
      <!-- Loading State -->
      <div v-if="filesStore.isLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="filesStore.error" class="text-center py-12">
        <p class="text-destructive">{{ filesStore.error }}</p>
      </div>

      <!-- Empty State -->
      <EmptyState v-else-if="trashedFiles.length === 0" :icon="Trash2" title="Trash is empty"
        description="Deleted files will appear here" action-text="Browse Files" @action="$router.push('/files')" />

      <!-- Files Display -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <FileCard v-for="file in trashedFiles" :key="file.id" :file="file" @preview="handlePreviewFile"
          @open-chat="handleOpenChat" @toggle-star="handleToggleStar" />
      </div>
    </div>

    <!-- Modals -->
    <UploadModal :is-open="isUploadOpen" @close="isUploadOpen = false" />
    <FilePreviewModal :is-open="isPreviewOpen" :file="selectedFile" @close="isPreviewOpen = false"
      @open-chat="handleOpenChat" />
  </div>
</template>
