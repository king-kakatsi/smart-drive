<script setup>
import { User, Bot } from 'lucide-vue-next'
import { cn } from '@/utils/cn'

const props = defineProps({
    message: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <div :class="cn(
        'flex gap-3 max-w-[85%]',
        message.role === 'user' ? 'ml-auto flex-row-reverse' : ''
    )">
        <div :class="cn(
            'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
            message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
        )">
            <User v-if="message.role === 'user'" class="w-4 h-4" />
            <Bot v-else class="w-4 h-4" />
        </div>

        <div class="space-y-1">
            <div :class="cn(
                'p-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap',
                message.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-none'
                    : 'bg-muted text-foreground rounded-tl-none'
            )">
                {{ message.content }}

                <!-- Sources -->
                <div v-if="message.sources && message.sources.length > 0" class="mt-3 pt-3 border-t border-border/50">
                    <p class="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Sources</p>
                    <div class="flex flex-wrap gap-2">
                        <div v-for="(source, index) in message.sources" :key="index" 
                             class="flex items-center gap-1.5 px-2 py-1 rounded bg-background/50 border border-border/50 text-[10px]">
                            <span class="font-medium truncate max-w-[120px]">{{ source.filename }}</span>
                            <span v-if="source.timestamp_range" class="text-secondary font-mono">{{ source.timestamp_range }}</span>
                            <span v-else-if="source.chunk_id !== undefined" class="text-muted-foreground">Chunk {{ source.chunk_id + 1 }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <p :class="cn('text-[10px] text-muted-foreground', message.role === 'user' ? 'text-right' : 'text-left')">
                {{ message.timestamp }}
            </p>
        </div>
    </div>
</template>
