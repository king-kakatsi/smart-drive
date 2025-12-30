<script setup>
import { cn } from '@/utils/cn'
import { X } from 'lucide-vue-next'

const props = defineProps({
  isOpen: Boolean,
  class: String
})

const emit = defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <Transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0"
      enter-to-class="opacity-100" leave-active-class="transition duration-150 ease-in" leave-from-class="opacity-100"
      leave-to-class="opacity-0">
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/80" @click="emit('close')" />

        <!-- Content -->
        <div
          :class="cn('relative z-50 grid w-full max-w-lg gap-4 border bg-background p-6 shadow-lg duration-200 sm:rounded-lg', props.class)">
          <slot />

          <button
            class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none"
            @click="emit('close')">
            <X class="h-4 w-4" />
            <span class="sr-only">Close</span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { cn } from '@/utils/cn'

export const ModalHeader = {
  props: ['class'],
  template: `
    <div :class="cn('flex flex-col space-y-1.5 text-center sm:text-left', $props.class)">
      <slot />
    </div>
  `
}

export const ModalTitle = {
  props: ['class'],
  template: `
    <h2 :class="cn('text-lg font-semibold leading-none tracking-tight', $props.class)">
      <slot />
    </h2>
  `
}

export const ModalDescription = {
  props: ['class'],
  template: `
    <p :class="cn('text-sm text-muted-foreground', $props.class)">
      <slot />
    </p>
  `
}

export const ModalFooter = {
  props: ['class'],
  template: `
    <div :class="cn('flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2', $props.class)">
      <slot />
    </div>
  `
}
</script>
