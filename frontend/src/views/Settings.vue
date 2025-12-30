<script setup>
import { ref, onMounted } from 'vue'
import { User, Bell, Shield, Cloud, Moon, Sun, LogOut } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useFilesStore } from '@/stores/files'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'
import { computed } from 'vue'

const uiStore = useUIStore()
const authStore = useAuthStore()
const filesStore = useFilesStore()

const user = computed(() => authStore.user || {
  full_name: 'User',
  email: ''
})

const userInitials = computed(() => {
  if (!user.value.full_name) return 'U'
  return user.value.full_name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2)
})

const storagePercentage = computed(() => {
  const metrics = filesStore.storageMetrics
  if (!metrics || metrics.total === 0) return 0
  return (metrics.used / metrics.total) * 100
})

const storageGB = computed(() => (filesStore.storageMetrics.used / (1024 * 1024 * 1024)).toFixed(1))
const totalGB = computed(() => (filesStore.storageMetrics.total / (1024 * 1024 * 1024)).toFixed(0))

const handleLogout = async () => {
  await authStore.logout()
}
</script>

<template>
  <div class="p-6 lg:p-12 max-w-2xl mx-auto space-y-10">
    <!-- Header -->
    <div class="text-center space-y-2">
      <h1 class="text-4xl font-black tracking-tight">Account</h1>
      <p class="text-muted-foreground font-medium">Manage your subscription and storage.</p>
    </div>

    <!-- Account Details Card -->
    <div class="space-y-8">
      <!-- Storage Section -->
      <section class="space-y-4">
        <div class="flex items-center justify-between px-2">
          <h2 class="text-lg font-bold flex items-center gap-2">
            <Cloud class="w-5 h-5 text-primary" />
            Cloud Storage
          </h2>
          <span class="text-sm font-black text-primary bg-primary/10 px-3 py-1 rounded-full">
            {{ storagePercentage.toFixed(0) }}% Used
          </span>
        </div>
        
        <div class="p-8 rounded-[2.5rem] bg-slate-100/50 dark:bg-slate-900/50 backdrop-blur-xl border border-white/10 shadow-xl space-y-6">
          <div class="relative h-3 w-full bg-muted/30 rounded-full overflow-hidden">
            <div
              class="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-secondary transition-all duration-1000 ease-out rounded-full shadow-[0_0_15px_rgba(37,99,235,0.4)]"
              :style="{ width: `${storagePercentage}%` }" />
          </div>
          <div class="flex justify-between items-end">
            <div class="space-y-1">
              <p class="text-2xl font-black">{{ storageGB }} GB</p>
              <p class="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">Total Used</p>
            </div>
            <p class="text-sm font-bold text-muted-foreground pb-1">
              of {{ totalGB }} GB available
            </p>
          </div>
        </div>
      </section>

      <!-- Profile Card -->
      <section class="space-y-4">
        <h2 class="text-lg font-bold px-2 flex items-center gap-2">
          <User class="w-5 h-5 text-primary" />
          Profile Details
        </h2>
        
        <div class="p-6 rounded-[2rem] bg-white/40 dark:bg-white/5 border border-white/10 backdrop-blur-md flex items-center gap-6">
          <div class="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary to-secondary p-[3px] shadow-2xl">
            <div class="w-full h-full bg-background rounded-[21px] flex items-center justify-center text-2xl font-black text-primary">
              {{ userInitials }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xl font-black truncate">{{ user.full_name }}</p>
            <p class="text-sm font-medium text-muted-foreground truncate opacity-70">{{ user.email }}</p>
            <div class="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-green-500/10 text-green-500 text-[10px] font-black uppercase tracking-wider">
              <Shield class="w-3 h-3" />
              Verified Premium
            </div>
          </div>
        </div>
      </section>

      <!-- Actions -->
      <div class="pt-6 space-y-4">
        <BaseButton variant="destructive" class="w-full py-8 rounded-[2rem] gap-3 shadow-2xl shadow-destructive/20 text-lg font-black transition-all hover:scale-[1.02] active:scale-95" @click="handleLogout">
          <LogOut class="w-6 h-6" />
          Sign Out of Smart Drive
        </BaseButton>
        <p class="text-center text-[11px] font-bold text-muted-foreground/40 uppercase tracking-[0.2em]">
          Version 2.4.0 • Secure Encryption Active
        </p>
      </div>
    </div>
  </div>
</template>
