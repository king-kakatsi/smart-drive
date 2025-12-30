<script setup>
import { ref } from 'vue'
import { Cloud, CheckCircle2, AlertCircle, ArrowRight, ShieldCheck, Zap } from 'lucide-vue-next'
import BaseModal, { ModalHeader, ModalTitle, ModalDescription } from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps({
    isOpen: Boolean
})

const emit = defineEmits(['close', 'connected'])

const isConnecting = ref(false)
const isConnected = ref(false)

const handleConnect = () => {
    isConnecting.value = true
    // Simulate connection process
    setTimeout(() => {
        isConnecting.value = false
        isConnected.value = true
        emit('connected')
    }, 2000)
}

const handleClose = () => {
    isConnected.value = false
    emit('close')
}
</script>

<template>
    <BaseModal :is-open="isOpen" @close="handleClose" class="max-w-md">
        <div v-if="!isConnected" class="py-4 space-y-6">
            <ModalHeader class="text-center sm:text-center">
                <div class="mx-auto w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
                    <Cloud class="w-8 h-8 text-primary" />
                </div>
                <ModalTitle class="text-2xl">Connect Google Drive</ModalTitle>
                <ModalDescription class="text-base">
                    Sync your files directly from Google Drive to analyze them with Smart-Drive AI.
                </ModalDescription>
            </ModalHeader>

            <div class="space-y-4">
                <div class="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-border">
                    <ShieldCheck class="w-5 h-5 text-primary shrink-0 mt-0.5" />
                    <div>
                        <p class="text-sm font-medium">Secure Access</p>
                        <p class="text-xs text-muted-foreground">We only request read-only access to your files.</p>
                    </div>
                </div>

                <div class="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-border">
                    <Zap class="w-5 h-5 text-secondary shrink-0 mt-0.5" />
                    <div>
                        <p class="text-sm font-medium">Real-time Sync</p>
                        <p class="text-xs text-muted-foreground">Changes in Drive are automatically reflected here.</p>
                    </div>
                </div>
            </div>

            <div class="space-y-3 pt-2">
                <BaseButton class="w-full h-12 text-base gap-2 shadow-md" :disabled="isConnecting"
                    @click="handleConnect">
                    <span v-if="isConnecting">Connecting...</span>
                    <template v-else>
                        Connect Google Drive
                        <ArrowRight class="w-4 h-4" />
                    </template>
                </BaseButton>

                <BaseButton variant="ghost" class="w-full" @click="handleClose">
                    Maybe later
                </BaseButton>
            </div>

            <p class="text-[10px] text-center text-muted-foreground">
                Your data is encrypted and secure. We never share your information with third parties.
            </p>
        </div>

        <div v-else class="py-12 text-center space-y-6">
            <div class="flex justify-center">
                <div
                    class="w-20 h-20 rounded-full bg-green-500/10 flex items-center justify-center animate-in zoom-in duration-300">
                    <CheckCircle2 class="w-10 h-10 text-green-500" />
                </div>
            </div>
            <div>
                <h3 class="text-xl font-bold mb-2">Successfully Connected!</h3>
                <p class="text-sm text-muted-foreground max-w-[250px] mx-auto">
                    Your Google Drive is now synced with Smart-Drive. You can start analyzing your files.
                </p>
            </div>
            <BaseButton class="px-8" @click="handleClose">
                Done
            </BaseButton>
        </div>
    </BaseModal>
</template>
