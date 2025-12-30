<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  LayoutDashboard,
  Folder,
  MessageSquare,
  User
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'

const route = useRoute()

const navItems = [
  { name: 'Home', icon: LayoutDashboard, path: '/' },
  { name: 'Files', icon: Folder, path: '/files' },
  { name: 'Chat', icon: MessageSquare, path: '/chat' },
  { name: 'Profile', icon: User, path: '/settings' },
]

const isActive = (path) => route.path === path
</script>

<template>
  <div
    class="fixed bottom-0 left-0 right-0 h-16 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-t border-white/10 flex items-center justify-around px-2 z-40">
    <router-link v-for="item in navItems" :key="item.name" :to="item.path" :class="cn(
      'flex flex-col items-center justify-center gap-1 flex-1 h-full transition-all duration-300',
      isActive(item.path) ? 'text-primary scale-110' : 'text-muted-foreground opacity-60 hover:opacity-100'
    )">
      <component :is="item.icon" class="w-5 h-5" />
      <span class="text-[10px] font-bold uppercase tracking-tighter">{{ item.name }}</span>
    </router-link>
  </div>
</template>
