<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFilesStore } from '@/stores/files'
import { useChatStore } from '@/stores/chat'
import { onMounted } from 'vue'
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

const router = useRouter()
const chatStore = useChatStore()

const isUploadOpen = ref(false)
const isDriveModalOpen = ref(false)
const isPreviewOpen = ref(false)
const selectedFile = ref(null)

const filesStore = useFilesStore()

onMounted(() => {
  if (authStore.isAuthenticated) {
    filesStore.fetchStorageMetrics()
    filesStore.fetchDriveFiles(10)
  }
})

const stats = computed(() => [
  { label: 'Total Files', value: filesStore.driveFiles.length.toString(), icon: HardDrive, color: 'bg-blue-500' },
  {
    label: 'Storage Used',
    value: `${(filesStore.storageMetrics.used / (1024 * 1024 * 1024)).toFixed(1)} GB`,
    icon: Cloud,
    color: 'bg-primary'
  },
  { label: 'AI Insights', value: '0', icon: MessageSquare, color: 'bg-secondary' },
  { label: 'Shared Files', value: '0', icon: Users, color: 'bg-purple-500' },
])

const recentFiles = computed(() => {
  return filesStore.driveFiles.slice(0, 3).map(file => ({
    id: file.id,
    name: file.name,
    type: file.mimeType?.split('/').pop() || 'file',
    size: file.size ? `${(parseInt(file.size) / (1024 * 1024)).toFixed(1)} MB` : 'Unknown',
    updatedAt: new Date(file.modifiedTime).toLocaleDateString(),
    isStarred: false
  }))
})

const handlePreviewFile = (file) => {
  selectedFile.value = file
  isPreviewOpen.value = true
}

const handleOpenChat = (file) => {
  chatStore.startChatWithFile(file)
  router.push('/chat')
}

const authStore = useAuthStore()
const firstName = computed(() => {
  const full_name = authStore.user?.full_name || 'User'
  return full_name.split(' ')[0]
})
</script>

<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto space-y-10">
    <!-- Premium Welcome Header -->
    <div
      class="relative overflow-hidden rounded-[2rem] p-8 lg:p-12 border border-white/20 shadow-2xl bg-slate-900 text-white">
      <!-- Decorative bg glow -->
      <div class="absolute -top-24 -right-24 w-96 h-96 bg-primary/30 blur-[120px] rounded-full animate-pulse" />
      <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-secondary/20 blur-[120px] rounded-full" />

      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
        <div>
          <div
            class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-xs font-bold uppercase tracking-wider mb-4">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-ping" />
            System Active
          </div>
          <h1 class="text-4xl lg:text-5xl font-black tracking-tight mb-4">
            Welcome back, <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">{{
              firstName }}</span>!
          </h1>
          <p class="text-slate-400 text-lg max-w-xl font-medium leading-relaxed">
            Your personal AI-powered drive is ready. You've used {{ ((filesStore.storageMetrics.used / (1024 * 1024 *
              1024)).toFixed(1)) }} GB of your storage.
          </p>
        </div>

        <!-- <div class="flex flex-wrap items-center gap-4">
          <button @click="isDriveModalOpen = true"
            class="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-white/10 hover:bg-white/20 backdrop-blur-xl border border-white/10 transition-all hover:scale-105 active:scale-95 font-bold">
            <Cloud class="w-5 h-5" />
            <span>Connect Drive</span>
          </button>
          <button @click="isUploadOpen = true"
            class="flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-primary text-primary-foreground shadow-xl shadow-primary/20 transition-all hover:scale-105 hover:shadow-primary/40 active:scale-95 font-bold">
            <Plus class="w-5 h-5" />
            <span>New Upload</span>
          </button>
        </div> -->
      </div>
    </div>

    <!-- Glassmorphism Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="stat in stats" :key="stat.label"
        class="backdrop-blur-md bg-white/40 dark:bg-slate-900/40 border border-white/20 dark:border-white/5 rounded-[1.8rem] p-6 hover:shadow-2xl hover:shadow-primary/5 transition-all group cursor-default">
        <div class="flex items-center justify-between mb-6">
          <div
            :class="cn('w-14 h-14 rounded-2xl flex items-center justify-center shadow-inner group-hover:scale-110 transition-all duration-500 relative', stat.color.replace('bg-', 'text-'))">
            <div :class="cn('absolute inset-0 opacity-20 rounded-2xl blur-lg', stat.color)" />
            <component :is="stat.icon" class="w-7 h-7 relative z-10" />
          </div>
          <div
            class="px-2 py-1 rounded-lg bg-green-500/10 text-green-500 text-[10px] font-black tracking-widest uppercase">
            LIVE
          </div>
        </div>
        <div class="space-y-1">
          <p class="text-3xl font-black tracking-tight text-foreground">{{ stat.value }}</p>
          <p class="text-sm text-muted-foreground font-bold uppercase tracking-widest opacity-70">{{ stat.label }}</p>
        </div>
      </div>
    </div>

    <!-- Premium Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div
        class="relative group overflow-hidden rounded-[2.5rem] p-1 border border-border/50 hover:border-primary/50 transition-colors cursor-pointer"
        @click="isUploadOpen = true">
        <div
          class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div
          class="relative bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm rounded-[2.4rem] p-10 flex flex-col items-center text-center">
          <div
            class="w-20 h-20 rounded-3xl bg-primary text-primary-foreground flex items-center justify-center mb-8 shadow-2xl shadow-primary/40 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
            <Plus class="w-10 h-10" />
          </div>
          <h3 class="text-2xl font-black mb-3 tracking-tight">Upload Content</h3>
          <p class="text-muted-foreground max-w-xs font-medium leading-relaxed">
            Ready to analyze something new? Drag and drop any file to get instant AI insights.
          </p>
        </div>
      </div>

      <div
        class="relative group overflow-hidden rounded-[2.5rem] p-1 border border-border/50 hover:border-secondary/50 transition-colors cursor-pointer"
        @click="router.push('/chat')">
        <div
          class="absolute inset-0 bg-gradient-to-br from-secondary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div
          class="relative bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm rounded-[2.4rem] p-10 flex flex-col items-center text-center">
          <div
            class="w-20 h-20 rounded-3xl bg-secondary text-secondary-foreground flex items-center justify-center mb-8 shadow-2xl shadow-secondary/40 group-hover:scale-110 group-hover:-rotate-3 transition-all duration-500">
            <MessageSquare class="w-10 h-10" />
          </div>
          <h3 class="text-2xl font-black mb-3 tracking-tight">AI Think Tank</h3>
          <p class="text-muted-foreground max-w-xs font-medium leading-relaxed">
            Jump back into your conversations or start a new deep-dive into your documents.
          </p>
        </div>
      </div>
    </div>

    <!-- Recent Activity Section -->
    <div class="space-y-6">
      <div class="flex items-center justify-between border-b border-border/50 pb-4">
        <h2 class="text-2xl font-black tracking-tight flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Clock class="w-5 h-5 text-primary" />
          </div>
          Recent Activity
        </h2>
        <router-link to="/files"
          class="group flex items-center gap-2 text-sm font-black text-primary hover:text-primary/80 transition-all">
          Browse Library
          <div
            class="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center group-hover:translate-x-1 transition-transform">
            <Plus class="w-3 h-3" />
          </div>
        </router-link>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
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
