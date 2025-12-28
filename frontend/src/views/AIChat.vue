<script setup>
import AIChatPanel from '@/components/chat/AIChatPanel.vue'
</script>

<template>
  <div class="h-full flex items-center justify-center bg-muted/10">
    <div class="w-full max-w-4xl h-[90vh] shadow-2xl rounded-2xl overflow-hidden border border-border">
      <AIChatPanel :is-open="true" @close="$router.back()" />
    </div>
  </div>
</template>
