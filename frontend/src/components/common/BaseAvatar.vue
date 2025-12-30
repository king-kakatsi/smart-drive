<script setup>
import { ref } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps({
  src: String,
  alt: String,
  class: String
})

const hasError = ref(false)
</script>

<template>
  <div :class="cn('relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full', props.class)">
    <img
      v-if="src && !hasError"
      :src="src"
      :alt="alt"
      class="aspect-square h-full w-full"
      @error="hasError = true"
    />
    <div
      v-else
      class="flex h-full w-full items-center justify-center rounded-full bg-muted"
    >
      <slot name="fallback">
        <span class="text-xs font-medium uppercase">
          {{ alt ? alt.charAt(0) : '?' }}
        </span>
      </slot>
    </div>
  </div>
</template>
