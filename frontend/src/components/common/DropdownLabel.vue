<script setup>
import { cn } from '@/utils/cn'

const props = defineProps({
    class: String
})
</script>

<template>
    <div :class="cn('px-2 py-1.5 text-sm font-semibold', props.class)">
        <slot />
    </div>
</template>
