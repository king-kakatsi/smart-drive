<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { X, Sparkles, Bot } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseButton from '@/components/common/BaseButton.vue'
import ScrollArea from '@/components/common/ScrollArea.vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'

const props = defineProps({
    isOpen: Boolean,
    selectedFile: Object
})

const emit = defineEmits(['close'])

const messages = ref([
    {
        id: 1,
        role: 'assistant',
        content: "Hello! I'm your AI assistant. I can help you analyze your documents and videos. What would you like to know?",
        timestamp: '10:00 AM'
    }
])

const scrollRef = ref(null)

const handleSendMessage = async (content) => {
    const userMessage = {
        id: Date.now(),
        role: 'user',
        content,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    messages.value.push(userMessage)

    await nextTick()
    scrollToBottom()

    // Simulate AI response
    setTimeout(async () => {
        const aiMessage = {
            id: Date.now() + 1,
            role: 'assistant',
            content: "I'm processing your request. This is a simulated response for the design demonstration.",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        messages.value.push(aiMessage)
        await nextTick()
        scrollToBottom()
    }, 1000)
}

const scrollToBottom = () => {
    if (scrollRef.value) {
        const scrollContainer = scrollRef.value.$el.querySelector('.overflow-auto')
        if (scrollContainer) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight
        }
    }
}

onMounted(() => {
    scrollToBottom()
})
</script>

<template>
    <div class="flex flex-col h-full w-full lg:w-96 bg-background border-l border-border shadow-xl">
        <!-- Header -->
        <div class="p-4 border-b border-border flex items-center justify-between bg-muted/30">
            <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
                    <Sparkles class="w-5 h-5" />
                </div>
                <div>
                    <h3 class="text-sm font-semibold">AI Assistant</h3>
                    <p class="text-[10px] text-muted-foreground flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                        Online & Ready
                    </p>
                </div>
            </div>
            <BaseButton variant="ghost" size="icon" @click="emit('close')">
                <X class="w-4 h-4" />
            </BaseButton>
        </div>

        <!-- Selected File Context -->
        <div v-if="selectedFile" class="p-3 bg-primary/5 border-b border-primary/10 flex items-center gap-3">
            <div class="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary">
                <Bot class="w-4 h-4" />
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-xs font-medium truncate">Analyzing: {{ selectedFile.name }}</p>
                <p class="text-[10px] text-muted-foreground">Context active</p>
            </div>
        </div>

        <!-- Messages -->
        <ScrollArea ref="scrollRef" class="flex-1 p-4">
            <div class="space-y-6">
                <ChatMessage v-for="message in messages" :key="message.id" :message="message" />
            </div>
        </ScrollArea>

        <!-- Input Area -->
        <ChatInput @send="handleSendMessage" />
    </div>
</template>
