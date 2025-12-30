<script setup>
import { provide, ref, watch } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps({
  modelValue: String,
  class: String
})

const emit = defineEmits(['update:modelValue'])

const activeTab = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  activeTab.value = val
})

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
import TabsList from './TabsList.vue'
import TabsTrigger from './TabsTrigger.vue'
import TabsContent from './TabsContent.vue'

export { TabsList, TabsTrigger, TabsContent }
</script>
