<script setup>
import { useUIStore } from '@/stores/ui'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import MobileNav from './MobileNav.vue'

const uiStore = useUIStore()
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-background">
    <!-- Desktop Sidebar -->
    <aside class="hidden lg:block">
      <AppSidebar />
    </aside>

    <!-- Mobile Sidebar Overlay -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="-translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="-translate-x-full"
    >
      <aside
        v-if="uiStore.isSidebarOpen"
        class="fixed inset-0 z-40 lg:hidden"
      >
        <div class="fixed inset-0 bg-black/50" @click="uiStore.toggleSidebar()" />
        <AppSidebar class="relative z-50" />
      </aside>
    </Transition>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <AppHeader />
      
      <main class="flex-1 overflow-y-auto pb-20 lg:pb-0">
        <slot />
      </main>
      
      <!-- Mobile Bottom Nav -->
      <MobileNav class="lg:hidden" />
    </div>
  </div>
</template>
