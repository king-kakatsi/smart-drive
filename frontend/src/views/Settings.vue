<script setup>
import { ref } from 'vue'
import { User, Bell, Shield, Cloud, Moon, Sun } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'

const uiStore = useUIStore()

const settings = ref({
  name: 'John Doe',
  email: 'john@example.com',
  notifications: true,
  theme: 'dark'
})
</script>

<template>
  <div class="p-6 lg:p-8 max-w-4xl mx-auto space-y-8">
    <div>
      <h1 class="text-3xl font-bold tracking-tight mb-2">Settings</h1>
      <p class="text-muted-foreground">Manage your account settings and preferences.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Sidebar -->
      <div class="space-y-1">
        <button class="w-full flex items-center gap-3 px-4 py-2 rounded-lg bg-primary/10 text-primary font-medium">
          <User class="w-4 h-4" />
          Profile
        </button>
        <button
          class="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-muted-foreground hover:bg-muted transition-colors">
          <Bell class="w-4 h-4" />
          Notifications
        </button>
        <button
          class="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-muted-foreground hover:bg-muted transition-colors">
          <Shield class="w-4 h-4" />
          Security
        </button>
        <button
          class="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-muted-foreground hover:bg-muted transition-colors">
          <Cloud class="w-4 h-4" />
          Storage
        </button>
      </div>

      <!-- Content -->
      <div class="md:col-span-2 space-y-8">
        <!-- Profile Section -->
        <section class="space-y-4">
          <h2 class="text-xl font-semibold border-b pb-2">Profile Information</h2>
          <div class="flex items-center gap-6 py-4">
            <BaseAvatar alt="John Doe" class="h-20 w-20" />
            <BaseButton variant="outline">Change Avatar</BaseButton>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">Full Name</label>
              <BaseInput v-model="settings.name" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">Email Address</label>
              <BaseInput v-model="settings.email" type="email" />
            </div>
          </div>
        </section>

        <!-- Appearance Section -->
        <section class="space-y-4">
          <h2 class="text-xl font-semibold border-b pb-2">Appearance</h2>
          <div class="flex items-center justify-between p-4 rounded-xl border border-border bg-muted/30">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-background flex items-center justify-center">
                <Moon v-if="uiStore.theme === 'dark'" class="w-5 h-5" />
                <Sun v-else class="w-5 h-5" />
              </div>
              <div>
                <p class="text-sm font-medium">Dark Mode</p>
                <p class="text-xs text-muted-foreground">Adjust the theme of the application.</p>
              </div>
            </div>
            <BaseButton variant="outline" @click="uiStore.toggleTheme()">
              {{ uiStore.theme === 'dark' ? 'Switch to Light' : 'Switch to Dark' }}
            </BaseButton>
          </div>
        </section>

        <div class="flex justify-end gap-3 pt-4">
          <BaseButton variant="ghost">Cancel</BaseButton>
          <BaseButton class="px-8">Save Changes</BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>
