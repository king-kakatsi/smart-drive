<script setup>
import { FileText, ExternalLink } from 'lucide-vue-next'
import { cn } from '@/utils/cn'

const props = defineProps({
    source: {
        type: Object,
        required: true
    },
    class: String
})
</script>

<template>
    <div
        :class="cn('inline-flex items-center gap-1.5 px-2 py-1 rounded bg-muted/50 border border-border hover:bg-muted transition-colors cursor-pointer group', props.class)">
        <FileText class="w-3 h-3 text-muted-foreground group-hover:text-primary transition-colors" />
        <span class="text-[10px] font-medium truncate max-w-[100px]">{{ source.name }}</span>
        <ExternalLink class="w-2.5 h-2.5 text-muted-foreground/50" />
    </div>
</template>
