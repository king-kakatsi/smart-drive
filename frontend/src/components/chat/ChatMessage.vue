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
                'p-3 rounded-2xl text-sm leading-relaxed',
                message.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-none'
                    : 'bg-muted text-foreground rounded-tl-none'
            )">
                {{ message.content }}
            </div>
            <p :class="cn('text-[10px] text-muted-foreground', message.role === 'user' ? 'text-right' : 'text-left')">
                {{ message.timestamp }}
            </p>
        </div>
    </div>
</template>
