<script setup>
import AIChatPanel from '@/components/chat/AIChatPanel.vue'
</script>

<template>
  <div class="h-full">
    <AIChatPanel :is-open="true" @close="$router.back()" />
  </div>
</template>
