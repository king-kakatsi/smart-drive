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
  <div
    class="w-64 h-full bg-slate-100/90 dark:bg-slate-950/90 backdrop-blur-xl border-r border-white/10 flex flex-col relative z-50">
    <!-- Logo -->
    <div class="p-8">
      <div class="flex items-center gap-3 transition-transform hover:scale-105 group cursor-pointer">
        <div
          class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-primary-foreground shadow-lg shadow-primary/30 group-hover:rotate-6 transition-all">
          <Cloud class="w-6 h-6" />
        </div>
        <div class="flex flex-col">
          <span class="font-black text-xl tracking-tighter text-foreground">Smart Drive</span>
          <span class="text-[9px] font-bold uppercase tracking-[0.2em] text-primary/60">AI Powered</span>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 space-y-2 mt-4">
      <router-link v-for="item in navItems" :key="item.name" :to="item.path" :class="cn(
        'group flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all duration-300',
        isActive(item.path)
          ? 'bg-primary text-primary-foreground shadow-xl shadow-primary/20'
          : 'text-muted-foreground hover:bg-white/10 hover:text-foreground'
      )">
        <component :is="item.icon"
          :class="cn('w-5 h-5 transition-transform group-hover:scale-110', isActive(item.path) ? 'text-white' : 'text-primary/70')" />
        <span>{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- Bottom Section (Desktop Only) -->
    <div class="p-6 space-y-6 hidden lg:block border-t border-white/5">
      <!-- Storage Indicator -->
      <div
        class="relative p-5 rounded-3xl bg-white/5 dark:bg-slate-900/50 border border-white/10 group overflow-hidden">
        <div class="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
        <div class="relative z-10 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">Cloud Storage</span>
            <span class="text-[10px] font-black text-foreground">{{ storagePercentage.toFixed(0) }}%</span>
          </div>
          <div class="relative h-1.5 w-full bg-muted/30 rounded-full overflow-hidden">
            <div
              class="absolute inset-y-0 left-0 bg-primary transition-all duration-1000 ease-out rounded-full shadow-[0_0_10px_rgba(37,99,235,0.5)]"
              :style="{ width: `${storagePercentage}%` }" />
          </div>
          <p class="text-[11px] font-bold text-muted-foreground leading-tight">
            {{ storageGB }} GB <span class="opacity-40">/</span> {{ totalGB }} GB Used
          </p>
        </div>
      </div>

      <!-- User Information -->
      <div class="space-y-3">
        <!-- Profile -->
        <div
          class="flex items-center gap-3 p-3 rounded-2xl hover:bg-white/10 transition-all group cursor-pointer border border-transparent hover:border-white/5">
          <div
            class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary p-[2px] shadow-lg group-hover:rotate-3 transition-all">
            <div class="w-full h-full bg-sidebar rounded-[10px] flex items-center justify-center text-xs font-black">
              {{ userInitials }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-black truncate text-foreground">{{ user.full_name }}</p>
            <p class="text-[10px] font-medium text-muted-foreground truncate opacity-60">{{ user.email }}</p>
          </div>
        </div>

        <!-- Logout -->
        <button @click="handleLogout"
          class="w-full flex items-center gap-3 p-3 rounded-2xl text-destructive hover:bg-destructive/10 transition-all border border-transparent hover:border-destructive/20 group">
          <div
            class="w-10 h-10 rounded-xl bg-destructive/10 flex items-center justify-center transition-all group-hover:bg-destructive/20">
            <LogOut class="w-4 h-4" />
          </div>
          <span class="text-xs font-black">Sign Out</span>
        </button>
      </div>
    </div>
  </div>
</template>
