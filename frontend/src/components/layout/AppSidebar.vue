<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFilesStore } from '@/stores/files'
import { onMounted } from 'vue'
import {
  Home,
  Folder,
  Clock,
  Star,
  Trash2,
  Cloud,
  Settings,
  Plus,
  LayoutDashboard,
  LogOut,
  MessageSquare
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseButton from '@/components/common/BaseButton.vue'
import Progress from '@/components/common/Progress.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user || {
  full_name: 'User',
  email: ''
})

const userInitials = computed(() => {
  const name = user.value.full_name || 'User'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
})

const handleLogout = async () => {
  await authStore.handleLogout()
  router.push({ name: 'Login' })
}

const navItems = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { name: 'All Files', icon: Folder, path: '/files' },
  { name: 'Recent', icon: Clock, path: '/recent' },
  { name: 'Starred', icon: Star, path: '/starred' },
  { name: 'AI Chat', icon: MessageSquare, path: '/chat' },
  // { name: 'Trash', icon: Trash2, path: '/trash' },
]

const filesStore = useFilesStore()

onMounted(() => {
  if (authStore.isAuthenticated) {
    filesStore.fetchStorageMetrics()
  }
})

const storageGB = computed(() => {
  const bytes = filesStore.storageMetrics.used
  return (bytes / (1024 * 1024 * 1024)).toFixed(1)
})

const totalGB = computed(() => {
  const bytes = filesStore.storageMetrics.total
  return (bytes / (1024 * 1024 * 1024)).toFixed(0)
})

const storagePercentage = computed(() => {
  const used = filesStore.storageMetrics.used
  const total = filesStore.storageMetrics.total
  if (total === 0) return 0
  return (used / total) * 100
})

const isActive = (path) => route.path === path
</script>

<template>
  <div class="w-64 h-full bg-sidebar border-r border-sidebar-border flex flex-col">
    <!-- Logo -->
    <div class="p-6">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground">
          <Cloud class="w-5 h-5" />
        </div>
        <span class="font-bold text-xl tracking-tight">Smart-Drive</span>
      </div>
    </div>

    <!-- New File Button -->
    <div class="px-4 mb-6">
      <BaseButton class="w-full justify-start gap-2 h-11 shadow-md">
        <Plus class="w-5 h-5" />
        <span>New Upload</span>
      </BaseButton>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-2 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        :class="cn(
          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          isActive(item.path) 
            ? 'bg-sidebar-accent text-sidebar-accent-foreground' 
            : 'text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
        )"
      >
        <component :is="item.icon" class="w-4 h-4" />
        <span>{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- Bottom Section -->
    <div class="p-4 border-t border-sidebar-border space-y-4">
      <!-- Storage Indicator -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs font-medium">
          <span class="text-muted-foreground">Storage</span>
          <span>{{ storageGB }} GB of {{ totalGB }} GB</span>
        </div>
        <Progress :value="storagePercentage" class="h-2" />
      </div>

      <!-- User Profile -->
      <div
        class="flex items-center gap-3 p-3 rounded-lg hover:bg-sidebar-accent transition-colors cursor-pointer group relative"
        title="User Profile"
      >
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-secondary to-accent flex items-center justify-center text-white font-medium shadow-inner group-hover:scale-105 transition-transform">
          {{ userInitials }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">{{ user.full_name }}</p>
          <p class="text-xs text-muted-foreground truncate">{{ user.email }}</p>
        </div>
      </div>

      <!-- Logout Button -->
      <button
        @click="handleLogout"
        class="flex items-center gap-3 p-3 rounded-lg hover:bg-sidebar-accent transition-colors cursor-pointer group relative w-full text-left"
        title="Logout"
      >
        <div class="w-10 h-10 rounded-full bg-red-500 flex items-center justify-center text-white shadow-inner group-hover:scale-105 transition-transform">
          <LogOut class="w-4 h-4" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium">Logout</p>
          <p class="text-xs text-muted-foreground">Sign out of your account</p>
        </div>
      </button>
    </div>
  </div>
</template>
