<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { X, Sparkles, Bot } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { useChatStore } from '@/stores/chat'
import BaseButton from '@/components/common/BaseButton.vue'
import ScrollArea from '@/components/common/ScrollArea.vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import TypingIndicator from './TypingIndicator.vue'

const props = defineProps({
    isOpen: Boolean,
    selectedFile: Object
})

const emit = defineEmits(['close'])

const chatStore = useChatStore()
const { messages, isTyping, error, currentContext } = storeToRefs(chatStore)

const displayFile = computed(() => {
    const file = props.selectedFile || currentContext.value
    if (!file) return null
    return {
        ...file,
        name: file.name || file.original_filename || file.filename || file.title || 'Unnamed File'
    }
})

const scrollRef = ref(null)

const handleSendMessage = async (content) => {
    await chatStore.sendMessage(content)
    await nextTick()
    scrollToBottom()
}

const scrollToBottom = () => {
    if (scrollRef.value) {
        const scrollContainer = scrollRef.value.$el.querySelector('.overflow-auto')
        if (scrollContainer) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight
        }
    }
}

// Watch for new messages and auto-scroll
watch(() => messages.value.length, () => {
    nextTick(() => scrollToBottom())
})

// Watch for selected file changes
watch(() => props.selectedFile, (newFile) => {
    if (newFile) {
        chatStore.setContextFiles([newFile.id])
    } else {
        chatStore.clearContext()
    }
})

onMounted(() => {
    // Initialize WebSocket connection
    chatStore.initializeWebSocket()
    scrollToBottom()
})

onUnmounted(() => {
    // Cleanup WebSocket connection
    chatStore.disconnect()
})
</script>

<template>
    <div class="flex flex-col h-full w-full bg-background">
        <!-- Header -->
        <div class="p-4 border-b border-border flex items-center justify-between bg-muted/30">
            <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
                    <Sparkles class="w-5 h-5" />
                </div>
                <div>
                    <h3 class="text-sm font-semibold truncate max-w-[200px]">
                        {{ displayFile?.name || 'AI Assistant' }}
                    </h3>
                    <p class="text-[10px] text-muted-foreground flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                        Online & Ready
                    </p>
                </div>
            </div>
            <BaseButton variant="ghost" size="icon" @click="emit('close'); chatStore.clearHistory()">
                <X class="w-4 h-4" />
            </BaseButton>
        </div>

        <!-- Selected File Context Info -->
        <div v-if="displayFile" class="p-3 bg-primary/5 border-b border-primary/10 flex items-center gap-3">
            <div class="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary">
                <Bot class="w-4 h-4" />
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-xs font-medium truncate">Analyzing: {{ displayFile.name }}</p>
                <p class="text-[10px] text-muted-foreground">Context active</p>
            </div>
        </div>

        <!-- Messages -->
        <ScrollArea ref="scrollRef" class="flex-1 p-4">
            <div class="space-y-6">
                <ChatMessage v-for="message in messages" :key="message.id" :message="message" />
                <TypingIndicator v-if="isTyping" />
            </div>
        </ScrollArea>

        <!-- Input Area -->
        <ChatInput @send="handleSendMessage" />
    </div>
</template>
