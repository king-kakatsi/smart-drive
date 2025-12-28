<script setup>
import { Bot } from 'lucide-vue-next'
import { cn } from '@/utils/cn'

const props = defineProps({
    class: String
})
</script>

<template>
    <div :class="cn('flex gap-3 max-w-[85%]', props.class)">
        <div class="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center shrink-0">
            <Bot class="w-4 h-4" />
        </div>
        <div class="bg-muted text-foreground p-3 rounded-2xl rounded-tl-none flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-muted-foreground/40 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
            <span
                class="w-1.5 h-1.5 bg-muted-foreground/40 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
            <span class="w-1.5 h-1.5 bg-muted-foreground/40 rounded-full animate-bounce"></span>
        </div>
    </div>
</template>
