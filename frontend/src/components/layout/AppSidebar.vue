<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  Home, 
  Folder, 
  Clock, 
  Star, 
  Trash2, 
  Cloud, 
  Settings, 
  Plus, 
  LayoutDashboard 
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseButton from '@/components/common/BaseButton.vue'
import Progress from '@/components/common/Progress.vue'

const route = useRoute()

const navItems = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { name: 'All Files', icon: Folder, path: '/files' },
  { name: 'Recent', icon: Clock, path: '/recent' },
  { name: 'Starred', icon: Star, path: '/starred' },
  { name: 'Trash', icon: Trash2, path: '/trash' },
]

const storageUsed = 12.4
const totalGB = 15
const storageGB = storageUsed.toFixed(1)
const storagePercentage = (storageUsed / totalGB) * 100

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
        <button class="w-full px-4 py-2 text-sm rounded-lg border border-border hover:bg-accent/10 transition-colors">
          Upgrade Plan
        </button>
      </div>

      <!-- User Profile -->
      <div class="flex items-center gap-3 p-3 rounded-lg hover:bg-sidebar-accent transition-colors cursor-pointer">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-secondary to-accent flex items-center justify-center text-white font-medium">
          JD
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">John Doe</p>
          <p class="text-xs text-muted-foreground truncate">john@example.com</p>
        </div>
      </div>
    </div>
  </div>
</template>
