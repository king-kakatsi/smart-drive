<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Menu, MessageSquare } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useFilesStore } from '@/stores/files'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'

const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()
const filesStore = useFilesStore()

const user = computed(() => authStore.user || {
  full_name: 'User'
})

const showSearch = computed(() => {
  const hiddenOn = ['Dashboard', 'AIChat']
  return !hiddenOn.includes(router.currentRoute.value.name)
})

// Redirect to files view when searching from other pages
import { watch } from 'vue'
watch(() => filesStore.searchQuery, (query) => {
  if (query && !['FileExplorer', 'Recent', 'Starred', 'Trash', 'Dashboard'].includes(router.currentRoute.value.name)) {
    router.push('/files')
  }
})
</script>

<template>
  <header
    class="h-20 backdrop-blur-xl bg-white/70 dark:bg-slate-900/70 border-b border-white/20 dark:border-white/5 flex items-center justify-between px-6 lg:px-10 sticky top-0 z-40">
    <div class="flex items-center gap-6 flex-1 max-w-3xl">
      <BaseButton variant="ghost" size="icon" class="lg:hidden rounded-xl hover:bg-muted/50 transition-all"
        @click="uiStore.toggleSidebar()">
        <Menu class="w-5 h-5" />
      </BaseButton>

      <div v-if="showSearch" class="relative w-full max-w-xl hidden md:block group">
        <div
          class="absolute inset-0 bg-primary/5 rounded-2xl blur-md opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none" />
        <Search
          class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
        <input v-model="filesStore.searchQuery" placeholder="Search your intelligent drive..."
          class="w-full pl-12 pr-4 py-3 bg-muted/30 hover:bg-muted/50 focus:bg-background border border-transparent focus:border-primary/20 rounded-2xl text-sm font-medium transition-all outline-none" />
      </div>
    </div>

    <div class="flex items-center gap-3 lg:gap-5">
      <button @click="router.push('/chat')"
        class="p-2.5 rounded-xl text-muted-foreground hover:text-primary hover:bg-primary/10 transition-all group relative"
        title="AI Assistant">
        <MessageSquare class="w-5 h-5 transition-transform group-hover:scale-110" />
        <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full border-2 border-background" />
      </button>

      <div class="h-8 w-px bg-border/40 mx-2 hidden sm:block" />

      <div class="flex items-center gap-3 pl-2 group cursor-pointer transition-all hover:translate-x-1">
        <div class="text-right hidden sm:block">
          <p class="text-xs font-black text-foreground mb-0.5">{{ user.full_name }}</p>
          <p class="text-[9px] font-bold text-primary uppercase tracking-widest">Premium Member</p>
        </div>
        <BaseAvatar :alt="user.full_name" :src="user.avatar_url"
          class="h-10 w-10 border-2 border-white/20 dark:border-white/5 shadow-xl transition-all group-hover:scale-110 group-hover:border-primary/50" />
      </div>
    </div>
  </header>
</template>
