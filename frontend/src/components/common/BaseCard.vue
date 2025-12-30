<script setup>
import { cn } from '@/utils/cn'

const props = defineProps({
  class: String
})
</script>

<template>
  <div :class="cn('bg-card text-card-foreground flex flex-col gap-y-1.5 rounded-xl border shadow-sm', props.class)">
    <slot />
  </div>
</template>

<script>
export const CardHeader = {
  props: ['class'],
  template: `
    <div :class="cn('flex flex-col gap-y-1.5 px-6 pt-6', $props.class)">
      <slot />
    </div>
  `
}

export const CardTitle = {
  props: ['class'],
  template: `
    <div :class="cn('font-semibold leading-none tracking-tight', $props.class)">
      <slot />
    </div>
  `
}

export const CardDescription = {
  props: ['class'],
  template: `
    <div :class="cn('text-muted-foreground text-sm', $props.class)">
      <slot />
    </div>
  `
}

export const CardContent = {
  props: ['class'],
  template: `
    <div :class="cn('px-6 [&:last-child]:pb-6', $props.class)">
      <slot />
    </div>
  `
}

export const CardFooter = {
  props: ['class'],
  template: `
    <div :class="cn('flex items-center px-6 pb-6 [.border-t]:pt-6', $props.class)">
      <slot />
    </div>
  `
}
</script>
