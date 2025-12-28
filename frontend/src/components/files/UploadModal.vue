<script setup>
import { ref } from 'vue'
import { Upload, X, File, CheckCircle2, AlertCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseModal, { ModalHeader, ModalTitle, ModalDescription, ModalFooter } from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import Progress from '@/components/common/Progress.vue'

const props = defineProps({
    isOpen: Boolean
})

const emit = defineEmits(['close', 'upload-complete'])

const files = ref([])
const isDragging = ref(false)

const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files)
    addFiles(selectedFiles)
}

const handleDrop = (event) => {
    isDragging.value = false
    const droppedFiles = Array.from(event.dataTransfer.files)
    addFiles(droppedFiles)
}

const addFiles = (newFiles) => {
    const mappedFiles = newFiles.map(file => ({
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
        progress: 0,
        status: 'uploading'
    }))

    files.value = [...files.value, ...mappedFiles]

    // Simulate upload progress
    mappedFiles.forEach(file => {
        simulateUpload(file.id)
    })
}

const simulateUpload = (id) => {
    const interval = setInterval(() => {
        const file = files.value.find(f => f.id === id)
        if (file) {
            if (file.progress >= 100) {
                file.status = 'completed'
                clearInterval(interval)
            } else {
                file.progress += Math.random() * 30
                if (file.progress > 100) file.progress = 100
            }
        }
    }, 500)
}

const removeFile = (id) => {
    files.value = files.value.filter(f => f.id !== id)
}

const handleClose = () => {
    files.value = []
    emit('close')
}
</script>

<template>
    <BaseModal :is-open="isOpen" @close="handleClose" class="max-w-xl">
        <ModalHeader>
            <ModalTitle>Upload Files</ModalTitle>
            <ModalDescription>
                Upload your documents, images, or videos to start analyzing them with AI.
            </ModalDescription>
        </ModalHeader>

        <div class="py-4 space-y-4">
            <!-- Dropzone -->
            <div :class="cn(
                'border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all cursor-pointer',
                isDragging ? 'border-primary bg-primary/5 scale-[0.99]' : 'border-border hover:border-primary/50 hover:bg-muted/30'
            )" @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                @click="$refs.fileInput.click()">
                <input ref="fileInput" type="file" multiple class="hidden" @change="handleFileSelect" />
                <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                    <Upload class="w-6 h-6 text-primary" />
                </div>
                <p class="text-sm font-medium mb-1">Click or drag files to upload</p>
                <p class="text-xs text-muted-foreground">Support for PDF, DOCX, MP4, MP3, and more</p>
            </div>

            <!-- File List -->
            <div v-if="files.length > 0" class="space-y-3 max-h-60 overflow-y-auto pr-2">
                <div v-for="file in files" :key="file.id"
                    class="p-3 rounded-lg border border-border bg-muted/30 space-y-2">
                    <div class="flex items-center justify-between gap-3">
                        <div class="flex items-center gap-3 min-w-0">
                            <div class="w-8 h-8 rounded bg-background flex items-center justify-center shrink-0">
                                <File class="w-4 h-4 text-muted-foreground" />
                            </div>
                            <div class="min-w-0">
                                <p class="text-xs font-medium truncate">{{ file.name }}</p>
                                <p class="text-[10px] text-muted-foreground">{{ file.size }}</p>
                            </div>
                        </div>

                        <div class="flex items-center gap-2">
                            <CheckCircle2 v-if="file.status === 'completed'" class="w-4 h-4 text-green-500" />
                            <button v-else class="p-1 hover:bg-background rounded transition-colors"
                                @click.stop="removeFile(file.id)">
                                <X class="w-4 h-4 text-muted-foreground" />
                            </button>
                        </div>
                    </div>

                    <div class="space-y-1">
                        <Progress :value="file.progress" class="h-1.5" />
                        <p class="text-[10px] text-muted-foreground">
                            {{ file.status === 'completed' ? 'Upload completed' : `Uploading...
                            ${Math.round(file.progress)}%` }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <ModalFooter v-if="files.length > 0 && files.every(f => f.status === 'completed')">
            <BaseButton class="w-full sm:w-auto px-8" @click="handleClose">
                Done
            </BaseButton>
        </ModalFooter>
    </BaseModal>
</template>
