<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  LayoutDashboard, 
  Folder, 
  MessageSquare, 
  Settings, 
  Plus 
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'

const route = useRoute()

const navItems = [
  { name: 'Home', icon: LayoutDashboard, path: '/' },
  { name: 'Files', icon: Folder, path: '/files' },
  { name: 'Chat', icon: MessageSquare, path: '/chat' },
  { name: 'Settings', icon: Settings, path: '/settings' },
]

const isActive = (path) => route.path === path
</script>

<template>
  <div class="fixed bottom-0 left-0 right-0 h-16 bg-background border-t border-border flex items-center justify-around px-2 z-40">
    <router-link
      v-for="item in navItems"
      :key="item.name"
      :to="item.path"
      :class="cn(
        'flex flex-col items-center justify-center gap-1 flex-1 h-full transition-colors',
        isActive(item.path) ? 'text-primary' : 'text-muted-foreground'
      )"
    >
      <component :is="item.icon" class="w-5 h-5" />
      <span class="text-[10px] font-medium">{{ item.name }}</span>
    </router-link>
    
    <!-- Floating Action Button for Mobile -->
    <button class="absolute -top-6 left-1/2 -translate-x-1/2 w-12 h-12 bg-primary text-primary-foreground rounded-full shadow-lg flex items-center justify-center border-4 border-background">
      <Plus class="w-6 h-6" />
    </button>
  </div>
</template>
