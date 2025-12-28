<script setup>
import { provide, ref } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps({
  modelValue: String,
  class: String
})

const emit = defineEmits(['update:modelValue'])

const activeTab = ref(props.modelValue)

provide('activeTab', activeTab)
provide('setActiveTab', (value) => {
  activeTab.value = value
  emit('update:modelValue', value)
})
</script>

<template>
  <div :class="cn('w-full', props.class)">
    <slot />
  </div>
</template>

<script>
import { inject, computed } from 'vue'
import { cn } from '@/utils/cn'

export const TabsList = {
  props: ['class'],
  template: `
    <div :class="cn('inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground', $props.class)">
      <slot />
    </div>
  `
}

export const TabsTrigger = {
  props: ['value', 'class'],
  setup(props) {
    const activeTab = inject('activeTab')
    const setActiveTab = inject('setActiveTab')
    
    const isActive = computed(() => activeTab.value === props.value)
    
    return { isActive, setActiveTab, cn }
  },
  template: `
    <button
      type="button"
      :class="cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        isActive ? 'bg-background text-foreground shadow' : 'hover:bg-background/50',
        $props.class
      )"
      @click="setActiveTab(value)"
    >
      <slot />
    </button>
  `
}

export const TabsContent = {
  props: ['value', 'class'],
  setup(props) {
    const activeTab = inject('activeTab')
    const isActive = computed(() => activeTab.value === props.value)
    
    return { isActive, cn }
  },
  template: `
    <div
      v-if="isActive"
      :class="cn('mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2', $props.class)"
    >
      <slot />
    </div>
  `
}
</script>
