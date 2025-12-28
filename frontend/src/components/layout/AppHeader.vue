<script setup>
import { Search, Bell, Menu, MessageSquare } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'

const uiStore = useUIStore()
</script>

<template>
  <header class="h-16 border-b border-border bg-background flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30">
    <div class="flex items-center gap-4 flex-1 max-w-2xl">
      <BaseButton
        variant="ghost"
        size="icon"
        class="lg:hidden"
        @click="uiStore.toggleSidebar()"
      >
        <Menu class="w-5 h-5" />
      </BaseButton>
      
      <div class="relative w-full max-w-md hidden md:block">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <BaseInput
          placeholder="Search files or ask AI..."
          class="pl-10 bg-muted/50 border-none focus-visible:ring-1"
        />
      </div>
    </div>

    <div class="flex items-center gap-2 lg:gap-4">
      <BaseButton
        variant="ghost"
        size="icon"
        class="text-muted-foreground hover:text-foreground"
        @click="uiStore.toggleChat()"
      >
        <MessageSquare class="w-5 h-5" />
      </BaseButton>
      
      <BaseButton
        variant="ghost"
        size="icon"
        class="text-muted-foreground hover:text-foreground"
      >
        <Bell class="w-5 h-5" />
      </BaseButton>
      
      <div class="h-8 w-px bg-border mx-2 hidden sm:block" />
      
      <BaseAvatar
        alt="John Doe"
        class="h-8 w-8 cursor-pointer"
      />
    </div>
  </header>
</template>
