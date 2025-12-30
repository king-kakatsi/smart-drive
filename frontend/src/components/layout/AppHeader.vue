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
    class="h-16 border-b border-border bg-background flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30">
    <div class="flex items-center gap-4 flex-1 max-w-2xl">
      <BaseButton variant="ghost" size="icon" class="lg:hidden" @click="uiStore.toggleSidebar()">
        <Menu class="w-5 h-5" />
      </BaseButton>

      <div class="relative w-full max-w-md hidden md:block">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <BaseInput v-model="filesStore.searchQuery" placeholder="Search files..."
          class="pl-10 bg-muted/50 border-none focus-visible:ring-1" />
      </div>
    </div>

    <div class="flex items-center gap-2 lg:gap-4">
      <BaseButton variant="ghost" size="icon" class="text-muted-foreground hover:text-foreground"
        @click="router.push('/chat')">
        <MessageSquare class="w-5 h-5" />
      </BaseButton>

      <div class="h-8 w-px bg-border mx-2 hidden sm:block" />

      <BaseAvatar :alt="user.full_name" :src="user.avatar_url" class="h-8 w-8 cursor-pointer" />
    </div>
  </header>
</template>
