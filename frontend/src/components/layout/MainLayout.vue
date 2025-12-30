<script setup>
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import MobileNav from './MobileNav.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-background">
    <!-- Desktop Sidebar -->
    <aside v-if="authStore.isAuthenticated" class="hidden lg:block">
      <AppSidebar />
    </aside>

    <!-- Mobile Sidebar Overlay -->
    <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0"
      enter-to-class="opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100"
      leave-to-class="opacity-0">
      <aside v-if="authStore.isAuthenticated && uiStore.isSidebarOpen" class="fixed inset-0 z-50 lg:hidden">
        <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="uiStore.toggleSidebar()" />
        <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="-translate-x-full"
          enter-to-class="translate-x-0" leave-active-class="transition duration-200 ease-in"
          leave-from-class="translate-x-0" leave-to-class="-translate-x-full">
          <AppSidebar v-if="uiStore.isSidebarOpen" class="relative z-50" />
        </Transition>
      </aside>
    </Transition>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <AppHeader v-if="authStore.isAuthenticated" />

      <main class="flex-1 overflow-y-auto pb-20 lg:pb-0">
        <slot />
      </main>

      <!-- Mobile Bottom Nav -->
      <MobileNav v-if="authStore.isAuthenticated" class="lg:hidden" />
    </div>
  </div>
</template>
