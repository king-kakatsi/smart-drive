<script setup>
import { ref } from 'vue'
import { Upload, X, File, CheckCircle2, AlertCircle, Loader2 } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseModal, { ModalHeader, ModalTitle, ModalDescription, ModalFooter } from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import Progress from '@/components/common/Progress.vue'
import { useFilesStore } from '@/stores/files'
import fileService from '@/services/api/fileService'

const props = defineProps({
    isOpen: Boolean
})

const emit = defineEmits(['close', 'upload-complete'])

const filesStore = useFilesStore()
const files = ref([])
const isDragging = ref(false)
const isUploadingAll = ref(false)

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
    const validFiles = newFiles.filter(file => {
        // Basic file type validation
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'video/mp4',
            'audio/mp3',
            'audio/mpeg',
            'image/jpeg',
            'image/png',
            'image/gif'
        ]
        const allowedExtensions = ['.pdf', '.docx', '.mp4', '.mp3', '.jpg', '.jpeg', '.png', '.gif']

        const hasValidType = allowedTypes.some(type => file.type.includes(type.split('/')[1]))
        const hasValidExtension = allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))

        return hasValidType || hasValidExtension
    })

    const mappedFiles = validFiles.map((file, index) => ({
        id: Math.random().toString(36).substr(2, 9),
        file: file, // Store the actual File object
        name: file.name,
        size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
        progress: 0,
        status: 'pending',
        error: null
    }))

    files.value = [...files.value, ...mappedFiles]
}

const uploadFile = async (fileId) => {
    const fileItem = files.value.find(f => f.id === fileId)
    if (!fileItem || !fileItem.file) return

    fileItem.status = 'uploading'
    fileItem.progress = 0

    try {
        // Upload using fileService
        const uploadedFile = await fileService.uploadFile(fileItem.file)

        fileItem.status = 'completed'
        fileItem.progress = 100

        // Update the files store to include the new file
        if (filesStore.fetchAllFiles) {
            await filesStore.fetchAllFiles()
        }

    } catch (error) {
        console.error('Upload failed:', error)
        fileItem.status = 'error'
        fileItem.error = error.message || 'Upload failed'
    }
}

const uploadAllFiles = async () => {
    if (isUploadingAll.value) return

    isUploadingAll.value = true
    const pendingFiles = files.value.filter(f => f.status === 'pending')

    try {
        // Upload files sequentially to avoid overwhelming the server
        for (const fileItem of pendingFiles) {
            await uploadFile(fileItem.id)
        }
    } catch (error) {
        console.error('Batch upload failed:', error)
    } finally {
        isUploadingAll.value = false
    }
}

const removeFile = (id) => {
    files.value = files.value.filter(f => f.id !== id)
}

const handleClose = () => {
    files.value = []
    emit('close')
}

const retryUpload = (id) => {
    const fileItem = files.value.find(f => f.id === id)
    if (fileItem) {
        fileItem.status = 'pending'
        fileItem.error = null
        uploadFile(id)
    }
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
                            <AlertCircle v-else-if="file.status === 'error'" class="w-4 h-4 text-red-500"
                                title="Upload failed" />
                            <Loader2 v-else-if="file.status === 'uploading'" class="w-4 h-4 animate-spin text-primary" />
                            <div v-else class="flex items-center gap-1">
                                <button v-if="file.status === 'error'" class="p-1 hover:bg-background rounded transition-colors"
                                    @click.stop="retryUpload(file.id)" title="Retry upload">
                                    <Upload class="w-3 h-3 text-muted-foreground" />
                                </button>
                                <button class="p-1 hover:bg-background rounded transition-colors"
                                    @click.stop="removeFile(file.id)">
                                    <X class="w-3 h-3 text-muted-foreground" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div v-if="file.status === 'uploading' || file.status === 'completed'" class="space-y-1">
                        <Progress :value="file.progress" class="h-1.5" />
                        <p class="text-[10px] text-muted-foreground">
                            {{ file.status === 'completed' ? 'Upload completed' :
                               `Uploading... ${Math.round(file.progress)}%` }}
                        </p>
                    </div>
                    <div v-if="file.status === 'error'" class="space-y-1">
                        <p class="text-[10px] text-red-500">{{ file.error }}</p>
                    </div>
                </div>
            </div>
        </div>

        <ModalFooter v-if="files.length > 0">
            <div class="flex gap-3 w-full sm:w-auto">
                <BaseButton
                    variant="outline"
                    class="flex-1 sm:flex-none"
                    @click="handleClose"
                    :disabled="isUploadingAll">
                    Cancel
                </BaseButton>
                <BaseButton
                    v-if="files.some(f => f.status === 'pending' || f.status === 'error')"
                    class="flex-1 sm:flex-none px-8"
                    @click="uploadAllFiles"
                    :disabled="isUploadingAll">
                    <Loader2 v-if="isUploadingAll" class="w-4 h-4 mr-2 animate-spin" />
                    {{ isUploadingAll ? 'Uploading...' : 'Upload Files' }}
                </BaseButton>
                <BaseButton
                    v-if="files.every(f => f.status === 'completed')"
                    class="flex-1 sm:flex-none px-8"
                    @click="handleClose">
                    Done
                </BaseButton>
            </div>
        </ModalFooter>
    </BaseModal>
</template>
