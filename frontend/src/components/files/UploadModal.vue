<script setup>
import { ref } from 'vue'
import { Upload, X, File, CheckCircle2, AlertCircle, Loader2 } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseModal, { ModalHeader, ModalTitle, ModalDescription } from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import Progress from '@/components/common/Progress.vue'
import { useFilesStore } from '@/stores/files'
import fileService from '@/services/api/fileService'
import driveService from '@/services/api/driveService'

const props = defineProps({
    isOpen: Boolean
})

const emit = defineEmits(['close', 'upload-complete'])

const filesStore = useFilesStore()
const files = ref([])
const isDragging = ref(false)
const isUploadingAll = ref(false)
const uploadDestination = ref('local')

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
        status: 'ready', // Files are ready to upload but not uploaded yet
        error: null
    }))

    files.value = [...files.value, ...mappedFiles]
}

const uploadFile = async (fileId) => {
    const fileItem = files.value.find(f => f.id === fileId)
    if (!fileItem || !fileItem.file) return

    fileItem.status = 'uploading'
    fileItem.progress = 0
    fileItem.error = null

    try {
        let uploadedFile

        // Choose upload service based on destination
        if (uploadDestination.value === 'local') {
            console.log('📤 Uploading to local storage:', fileItem.file.name)
            uploadedFile = await fileService.uploadFile(fileItem.file)
            console.log('✅ Local upload successful:', uploadedFile)
        } else if (uploadDestination.value === 'drive') {
            console.log('☁️ Uploading to Google Drive:', fileItem.file.name)
            uploadedFile = await driveService.uploadFileToDrive(fileItem.file)
            console.log('✅ Google Drive upload response:', uploadedFile)
        }

        fileItem.status = 'completed'
        fileItem.progress = 100

        // Update the files store based on upload destination
        console.log('🔄 Refreshing file list...')
        if (uploadDestination.value === 'local') {
            await filesStore.fetchAllFiles('/')
        } else if (uploadDestination.value === 'drive') {
            await filesStore.fetchDriveFiles()
        }
        console.log('📊 Files store updated after upload')

    } catch (error) {
        console.error('❌ Upload failed:', error)
        console.error('Error details:', error.message)
        console.error('Stack trace:', error.stack)
        fileItem.status = 'error'
        fileItem.error = error.message || 'Upload failed'
        fileItem.progress = 0
    }
}

const uploadAllFiles = async () => {
    if (isUploadingAll.value) return

    isUploadingAll.value = true
    const readyFiles = files.value.filter(f => f.status === 'ready' || f.status === 'error')

    try {
        // Upload files sequentially to avoid overwhelming the server
        for (const fileItem of readyFiles) {
            await uploadFile(fileItem.id)
        }

        // Check if all files completed successfully and close modal
        const allCompleted = files.value.every(f => f.status === 'completed')
        if (allCompleted) {
            emit('close')
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
    if (fileItem && fileItem.status === 'error') {
        fileItem.status = 'ready'
        fileItem.error = null
        fileItem.progress = 0
        // Don't auto-upload, let user click Submit
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

        <!-- Upload Destination Selection -->
        <div class="space-y-4 px-6 pt-4">
            <div class="space-y-2">
                <Label>Upload Destination</Label>
                <RadioGroup v-model="uploadDestination">
                    <div class="flex items-center space-x-2">
                        <RadioGroupItem value="local" id="local" />
                        <Label for="local">Local Storage</Label>
                    </div>
                    <div class="flex items-center space-x-2">
                        <RadioGroupItem value="drive" id="drive" />
                        <Label for="drive">Google Drive</Label>
                    </div>
                </RadioGroup>
            </div>
        </div>

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
                                <button class="p-1 hover:bg-background rounded transition-colors"
                                    @click.stop="removeFile(file.id)" title="Remove file">
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

            <!-- Submit and Cancel Buttons -->
            <div v-if="files.length > 0" class="flex gap-3 justify-end pt-4 border-t border-border">
                <BaseButton
                    variant="outline"
                    @click="handleClose"
                    :disabled="isUploadingAll">
                    Cancel
                </BaseButton>
                <BaseButton
                    v-if="!files.every(f => f.status === 'completed')"
                    @click="uploadAllFiles"
                    :disabled="isUploadingAll">
                    <Loader2 v-if="isUploadingAll" class="w-4 h-4 mr-2 animate-spin" />
                    {{ isUploadingAll ? 'Uploading...' : 'Submit' }}
                </BaseButton>
                <BaseButton
                    v-if="files.every(f => f.status === 'completed')"
                    @click="handleClose">
                    Done
                </BaseButton>
            </div>
        </div>
    </BaseModal>
</template>
