<script setup>
import { ref } from 'vue'
import { Send, Paperclip } from 'lucide-vue-next'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'

const props = defineProps({
    placeholder: {
        type: String,
        default: 'Ask about your documents...'
    }
})

const emit = defineEmits(['send'])

const inputValue = ref('')

const handleSend = () => {
    if (!inputValue.value.trim()) return
    emit('send', inputValue.value)
    inputValue.value = ''
}
</script>

<template>
    <div class="p-4 border-t border-border bg-muted/30">
        <div class="flex gap-2">
            <div class="relative flex-1">
                <BaseInput v-model="inputValue" :placeholder="placeholder"
                    class="pr-10 bg-background border-border rounded-xl" @keydown.enter="handleSend" />
                <button
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                    <Paperclip class="w-4 h-4" />
                </button>
            </div>
            <BaseButton size="icon" class="rounded-xl shrink-0" :disabled="!inputValue.trim()" @click="handleSend">
                <Send class="w-4 h-4" />
            </BaseButton>
        </div>
        <p class="text-[10px] text-center text-muted-foreground mt-3">
            AI can make mistakes. Verify important information.
        </p>
    </div>
</template>
