<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import FileExplorer from '@/components/files/FileExplorer.vue'
import UploadModal from '@/components/files/UploadModal.vue'
import FilePreviewModal from '@/components/files/FilePreviewModal.vue'

const router = useRouter()
const chatStore = useChatStore()

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
</script>

<template>
  <div class="h-full">
    <FileExplorer @open-chat="handleOpenChat" @show-upload="isUploadOpen = true" @preview-file="handlePreviewFile" />

    <!-- Modals -->
    <UploadModal :is-open="isUploadOpen" @close="isUploadOpen = false" />
    <FilePreviewModal :is-open="isPreviewOpen" :file="selectedFile" @close="isPreviewOpen = false"
      @open-chat="handleOpenChat" />
  </div>
</template>
