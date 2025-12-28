<script setup>
import { inject } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps({
    class: String,
    disabled: Boolean
})

const close = inject('closeDropdown')
</script>

<template>
    <div :class="cn(
        'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        props.class
    )" :data-disabled="disabled ? '' : undefined" @click="close">
        <slot />
    </div>
</template>
