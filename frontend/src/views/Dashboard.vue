<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  FileText,
  Video,
  Music,
  Image as ImageIcon,
  Plus,
  Cloud,
  MessageSquare,
  TrendingUp,
  Clock,
  HardDrive,
  Users
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseButton from '@/components/common/BaseButton.vue'
import FileCard from '@/components/files/FileCard.vue'
import UploadModal from '@/components/files/UploadModal.vue'
import GoogleDriveModal from '@/components/files/GoogleDriveModal.vue'
import FilePreviewModal from '@/components/files/FilePreviewModal.vue'

const isUploadOpen = ref(false)
const isDriveModalOpen = ref(false)
const isPreviewOpen = ref(false)
const selectedFile = ref(null)

const stats = [
  { label: 'Total Files', value: '1,284', icon: HardDrive, color: 'bg-blue-500' },
  { label: 'Storage Used', value: '12.4 GB', icon: Cloud, color: 'bg-primary' },
  { label: 'AI Insights', value: '42', icon: MessageSquare, color: 'bg-secondary' },
  { label: 'Shared Files', value: '156', icon: Users, color: 'bg-purple-500' },
]

const recentFiles = ref([
  { id: 1, name: 'Project Proposal.pdf', type: 'pdf', size: '2.4 MB', updatedAt: '2 hours ago', isStarred: true },
  { id: 2, name: 'Product Demo.mp4', type: 'mp4', size: '45.8 MB', updatedAt: '5 hours ago', isStarred: false },
  { id: 3, name: 'Design Assets.zip', type: 'zip', size: '12.1 MB', updatedAt: 'Yesterday', isStarred: false },
])

const handlePreviewFile = (file) => {
  selectedFile.value = file
  isPreviewOpen.value = true
}


const authStore = useAuthStore()
const firstName = computed(() => {
  const full_name = authStore.user?.full_name || 'User'
  return full_name.split(' ')[0]
})
</script>

<template>
  <div class="p-6 lg:p-8 max-w-7xl mx-auto space-y-8">
    <!-- Welcome Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight mb-2">Welcome back, {{ firstName }}!</h1>
        <p class="text-muted-foreground">Here's what's happening with your files today.</p>
      </div>
      <div class="flex items-center gap-3">
        <BaseButton variant="outline" class="gap-2" @click="isDriveModalOpen = true">
          <Cloud class="w-4 h-4" />
          <span>Connect Drive</span>
        </BaseButton>
        <BaseButton class="gap-2 shadow-md" @click="isUploadOpen = true">
          <Plus class="w-4 h-4" />
          <span>New Upload</span>
        </BaseButton>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="stat in stats" :key="stat.label"
        class="bg-card rounded-2xl border border-border p-6 hover:shadow-lg transition-all group">
        <div class="flex items-center justify-between mb-4">
          <div
            :class="cn('w-12 h-12 rounded-xl flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform', stat.color)">
            <component :is="stat.icon" class="w-6 h-6" />
          </div>
          <TrendingUp class="w-4 h-4 text-green-500" />
        </div>
        <p class="text-2xl font-bold mb-1">{{ stat.value }}</p>
        <p class="text-sm text-muted-foreground font-medium">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        class="bg-primary/5 border border-primary/10 rounded-2xl p-8 flex flex-col items-center text-center group hover:bg-primary/10 transition-colors cursor-pointer"
        @click="isUploadOpen = true">
        <div
          class="w-16 h-16 rounded-2xl bg-primary text-primary-foreground flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 transition-transform">
          <Plus class="w-8 h-8" />
        </div>
        <h3 class="text-xl font-bold mb-2">Upload New Content</h3>
        <p class="text-muted-foreground max-w-xs">Upload documents, videos, or audio files to get instant AI analysis.
        </p>
      </div>

      <div
        class="bg-secondary/5 border border-secondary/10 rounded-2xl p-8 flex flex-col items-center text-center group hover:bg-secondary/10 transition-colors cursor-pointer">
        <div
          class="w-16 h-16 rounded-2xl bg-secondary text-secondary-foreground flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 transition-transform">
          <MessageSquare class="w-8 h-8" />
        </div>
        <h3 class="text-xl font-bold mb-2">Start AI Chat</h3>
        <p class="text-muted-foreground max-w-xs">Ask questions about your entire library or specific documents.</p>
      </div>
    </div>

    <!-- Recent Files -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold flex items-center gap-2">
          <Clock class="w-5 h-5 text-primary" />
          Recent Files
        </h2>
        <router-link to="/files" class="text-sm font-medium text-primary hover:underline">View all files</router-link>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <FileCard v-for="file in recentFiles" :key="file.id" :file="file" @preview="handlePreviewFile"
          @open-chat="handleOpenChat" />
      </div>
    </div>

    <!-- Modals -->
    <UploadModal :is-open="isUploadOpen" @close="isUploadOpen = false" />
    <GoogleDriveModal :is-open="isDriveModalOpen" @close="isDriveModalOpen = false" />
    <FilePreviewModal :is-open="isPreviewOpen" :file="selectedFile" @close="isPreviewOpen = false"
      @open-chat="handleOpenChat" />
  </div>
</template>
