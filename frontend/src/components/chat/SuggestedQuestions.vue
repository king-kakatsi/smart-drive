<script setup>
import { MessageSquarePlus } from 'lucide-vue-next'
import { cn } from '@/utils/cn'

const props = defineProps({
    questions: {
        type: Array,
        default: () => []
    },
    class: String
})

const emit = defineEmits(['select'])
</script>

<template>
    <div :class="cn('flex flex-wrap gap-2', props.class)">
        <button v-for="(question, index) in questions" :key="index"
            class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-background border border-border text-xs font-medium text-muted-foreground hover:border-primary hover:text-primary hover:bg-primary/5 transition-all text-left"
            @click="emit('select', question)">
            <MessageSquarePlus class="w-3 h-3" />
            {{ question }}
        </button>
    </div>
</template>
