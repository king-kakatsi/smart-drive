<script setup>
import { cn } from '@/utils/cn'

const props = defineProps({
  class: String
})
</script>

<template>
  <div :class="cn('relative overflow-hidden', props.class)">
    <div class="h-full w-full overflow-auto scrollbar-hide">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
