<script setup>
import { inject, computed } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps({
    value: {
        type: String,
        required: true
    },
    class: String
})

const activeTab = inject('activeTab')
const setActiveTab = inject('setActiveTab')

const isActive = computed(() => activeTab.value === props.value)
</script>

<template>
    <button type="button" :class="cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        isActive ? 'bg-background text-foreground shadow' : 'hover:bg-background/50',
        props.class
    )" @click="setActiveTab(value)">
        <slot />
    </button>
</template>
