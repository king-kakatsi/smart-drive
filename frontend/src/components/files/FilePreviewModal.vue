<script setup>
import { computed } from 'vue'
import {
    X,
    MessageSquare,
    Download,
    Trash2,
    Share2,
    FileText,
    Video,
    Music,
    Image as ImageIcon,
    File,
    Folder,
    Clock,
    HardDrive,
    Info
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps({
    isOpen: Boolean,
    file: Object
})

const emit = defineEmits(['close', 'open-chat', 'download', 'delete', 'share'])

const getFileIcon = (file) => {
    // Handle both file.type and file.mimeType
    // Check for Google Drive folder first
    if (file.mimeType === 'application/vnd.google-apps.folder' ||
        file.type === 'folder' ||
        file.file_type === 'folder') {
        return Folder
    }

    // Unified type extraction
    const rawType = file.file_type || file.type || ''
    const mime = (file.mimeType || file.mime_type || '').split('/').pop() || ''
    const extension = (file.original_filename || file.name || '').split('.').pop() || ''
    
    const type = (rawType || mime || extension || 'file').toLowerCase()

    if (type.includes('pdf')) return FileText
    if (['doc', 'docx', 'word', 'document'].some(t => type.includes(t))) return FileText
    if (['txt', 'text', 'markdown', 'md'].some(t => type.includes(t))) return FileText
    
    if (['mp4', 'mov', 'avi', 'video'].some(t => type.includes(t))) return Video
    if (['mp3', 'wav', 'audio'].some(t => type.includes(t))) return Music
    
    if (['jpg', 'jpeg', 'png', 'gif', 'image'].some(t => type.includes(t))) return ImageIcon
    
    return File
}

const getIconColor = (file) => {
    // Check for Google Drive folder first
    if (file.mimeType === 'application/vnd.google-apps.folder' ||
        file.type === 'folder' ||
        file.file_type === 'folder') {
        return 'text-yellow-600'
    }

    // Unified type extraction
    const rawType = file.file_type || file.type || ''
    const mime = (file.mimeType || file.mime_type || '').split('/').pop() || ''
    const type = (rawType || mime || 'file').toLowerCase()

    if (type.includes('pdf')) return 'text-red-500'
    if (['doc', 'docx', 'word', 'document'].some(t => type.includes(t))) return 'text-blue-500'
    
    if (['mp4', 'mov', 'video'].some(t => type.includes(t))) return 'text-purple-500'
    if (['mp3', 'wav', 'audio'].some(t => type.includes(t))) return 'text-pink-500'
    
    if (['jpg', 'jpeg', 'png', 'gif', 'image'].some(t => type.includes(t))) return 'text-orange-500'
    
    return 'text-gray-500'
}

const previewUrl = computed(() => {
    if (!props.file) return null

    // 1. If it's a Drive file with a thumbnail, use it
    if (props.file.thumbnailLink) {
        // thumbnailLink is usually small, but we can try to get a larger one by removing =s220
        return props.file.thumbnailLink.replace(/=s\d+$/, '=s1000')
    }

    // 2. If it's a local file or synced file with local copy, use our preview endpoint
    const localId = props.file.local_id || (!isNaN(props.file.id) ? props.file.id : null)
    if (localId) {
        const token = localStorage.getItem('access_token')
        return `/api/v1/files/${localId}/preview?token=${token}`
    }

    // 3. Fallback to webViewLink for Drive files if nothing else
    if (props.file.webViewLink) {
        return props.file.webViewLink
    }

    return null
})

const isImage = computed(() => {
    const type = (props.file?.type || props.file?.mimeType?.split('/').pop() || '').toLowerCase()
    return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'image'].includes(type)
})

const isPDF = computed(() => {
    const type = (props.file?.type || props.file?.mimeType?.split('/').pop() || '').toLowerCase()
    return type === 'pdf'
})
</script>

<template>
    <BaseModal :is-open="isOpen" @close="emit('close')" class="max-w-5xl p-0 overflow-hidden">
        <div v-if="file" class="flex flex-col lg:flex-row h-[80vh]">
            <!-- Preview Area -->
            <div class="flex-1 bg-muted/30 flex items-center justify-center p-8 relative overflow-hidden">
                <div
                    class="absolute top-4 left-4 flex items-center gap-2 bg-background/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-border shadow-sm">
                    <component :is="getFileIcon(file)" :class="cn('w-4 h-4', getIconColor(file))" />
                    <span class="text-xs font-medium">{{ file.name }}</span>
                </div>

                <!-- Preview Content -->
                <div class="w-full h-full flex items-center justify-center">
                    <template v-if="isImage && previewUrl">
                        <img :src="previewUrl"
                            class="max-w-full max-h-full rounded-lg shadow-2xl object-contain border border-white/10"
                            @error="(e) => e.target.src = ''" />
                    </template>
                    <template v-else-if="isPDF && previewUrl">
                         <iframe :src="previewUrl" class="w-full h-full rounded-lg border-0 bg-white" shadow-2xl></iframe>
                    </template>
                    <template v-else-if="(file.type || file.mimeType?.split('/').pop()) === 'mp4'">
                        <div
                            class="w-full aspect-video bg-black rounded-lg shadow-2xl flex items-center justify-center">
                            <Video class="w-20 h-20 text-white/20" />
                        </div>
                    </template>
                    <template v-else>
                        <div class="flex flex-col items-center gap-4">
                            <div
                                :class="cn('w-32 h-32 rounded-2xl bg-background shadow-xl flex items-center justify-center border border-border', getIconColor(file))">
                                <component :is="getFileIcon(file)" class="w-16 h-16" />
                            </div>
                            <p class="text-muted-foreground text-sm">Preview not available for this file type</p>
                            <BaseButton v-if="file.webViewLink" variant="outline" size="sm" @click="window.open(file.webViewLink, '_blank')">
                                View on Google Drive
                            </BaseButton>
                        </div>
                    </template>
                </div>
            </div>

            <!-- Info Sidebar -->
            <div class="w-full lg:w-80 border-l border-border bg-background flex flex-col">
                <div class="p-6 border-b border-border">
                    <h2 class="text-lg font-semibold mb-1 truncate">{{ file.name }}</h2>
                    <p class="text-xs text-muted-foreground">{{ (file.type || file.mimeType?.split('/').pop() || 'FILE').toUpperCase() }} File • {{ file.size }}</p>
                </div>

                <div class="flex-1 overflow-y-auto p-6 space-y-8">
                    <!-- Quick Actions -->
                    <div class="space-y-3">
                        <div class="grid grid-cols-2 gap-2">
                            <BaseButton class="gap-2 bg-gray-900 text-accent-foreground hover:bg-gray-700" @click="emit('open-chat', file)">
                                <MessageSquare class="w-4 h-4" />
                                <span>Ask AI</span>
                            </BaseButton>
                            <BaseButton class="gap-2 bg-accent text-accent-foreground hover:bg-[#129989]" @click="emit('share', file)">
                                <Share2 class="w-4 h-4" />
                                <span>Share</span>
                            </BaseButton>
                            <BaseButton variant="outline" class="gap-2 border-secondary text-secondary hover:bg-secondary hover:text-accent-foreground" @click="emit('download', file)">
                                <Download class="w-4 h-4" />
                                <span>Download</span>
                            </BaseButton>
                        </div>
                    </div>

                    <!-- File Details -->
                    <div class="space-y-4">
                        <h3
                            class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                            <Info class="w-3 h-3" />
                            File Details
                        </h3>

                        <div class="space-y-3">
                            <div class="flex items-center justify-between text-sm">
                                <div class="flex items-center gap-2 text-muted-foreground">
                                    <Clock class="w-4 h-4" />
                                    <span>Modified</span>
                                </div>
                                <span class="font-medium">{{ file.updatedAt }}</span>
                            </div>
                            <div class="flex items-center justify-between text-sm">
                                <div class="flex items-center gap-2 text-muted-foreground">
                                    <HardDrive class="w-4 h-4" />
                                    <span>Size</span>
                                </div>
                                <span class="font-medium">{{ file.size }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="p-6 border-t border-border">
                    <BaseButton variant="outline" class="w-full border-pink-700 text-pink-700 hover:bg-pink-700 hover:text-white gap-2"
                        @click="emit('delete', file)">
                        <Trash2 class="w-4 h-4" />
                        <span>Delete File</span>
                    </BaseButton>
                </div>
            </div>
        </div>
    </BaseModal>
</template>
