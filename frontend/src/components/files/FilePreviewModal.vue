<script setup>
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

const getFileIcon = (type) => {
    switch (type?.toLowerCase()) {
        case 'pdf':
        case 'doc':
        case 'docx':
        case 'txt':
            return FileText
        case 'mp4':
        case 'mov':
        case 'avi':
            return Video
        case 'mp3':
        case 'wav':
            return Music
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
            return ImageIcon
        default:
            return File
    }
}

const getIconColor = (type) => {
    switch (type?.toLowerCase()) {
        case 'pdf': return 'text-red-500'
        case 'doc':
        case 'docx': return 'text-blue-500'
        case 'mp4':
        case 'mov': return 'text-purple-500'
        case 'mp3': return 'text-pink-500'
        case 'jpg':
        case 'png': return 'text-orange-500'
        default: return 'text-gray-500'
    }
}
</script>

<template>
    <BaseModal :is-open="isOpen" @close="emit('close')" class="max-w-5xl p-0 overflow-hidden">
        <div v-if="file" class="flex flex-col lg:flex-row h-[80vh]">
            <!-- Preview Area -->
            <div class="flex-1 bg-muted/30 flex items-center justify-center p-8 relative overflow-hidden">
                <div
                    class="absolute top-4 left-4 flex items-center gap-2 bg-background/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-border shadow-sm">
                    <component :is="getFileIcon(file.type)" :class="cn('w-4 h-4', getIconColor(file.type))" />
                    <span class="text-xs font-medium">{{ file.name }}</span>
                </div>

                <!-- Preview Content -->
                <div class="w-full h-full flex items-center justify-center">
                    <template v-if="file.type === 'jpg' || file.type === 'png'">
                        <img src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop"
                            class="max-w-full max-h-full rounded-lg shadow-2xl object-contain" />
                    </template>
                    <template v-else-if="file.type === 'mp4'">
                        <div
                            class="w-full aspect-video bg-black rounded-lg shadow-2xl flex items-center justify-center">
                            <Video class="w-20 h-20 text-white/20" />
                        </div>
                    </template>
                    <template v-else>
                        <div class="flex flex-col items-center gap-4">
                            <div
                                :class="cn('w-32 h-32 rounded-2xl bg-background shadow-xl flex items-center justify-center border border-border', getIconColor(file.type))">
                                <component :is="getFileIcon(file.type)" class="w-16 h-16" />
                            </div>
                            <p class="text-muted-foreground text-sm">Preview not available for this file type</p>
                        </div>
                    </template>
                </div>
            </div>

            <!-- Info Sidebar -->
            <div class="w-full lg:w-80 border-l border-border bg-background flex flex-col">
                <div class="p-6 border-b border-border">
                    <h2 class="text-lg font-semibold mb-1 truncate">{{ file.name }}</h2>
                    <p class="text-xs text-muted-foreground">{{ file.type.toUpperCase() }} File • {{ file.size }}</p>
                </div>

                <div class="flex-1 overflow-y-auto p-6 space-y-8">
                    <!-- Quick Actions -->
                    <div class="space-y-3">
                        <BaseButton class="w-full justify-start gap-3 h-12 shadow-sm" @click="emit('open-chat', file)">
                            <MessageSquare class="w-5 h-5" />
                            <span>Ask AI about this file</span>
                        </BaseButton>

                        <div class="grid grid-cols-2 gap-2">
                            <BaseButton variant="outline" class="gap-2" @click="emit('share', file)">
                                <Share2 class="w-4 h-4" />
                                <span>Share</span>
                            </BaseButton>
                            <BaseButton variant="outline" class="gap-2" @click="emit('download', file)">
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
                    <BaseButton variant="ghost" class="w-full text-destructive hover:bg-destructive/10 gap-2"
                        @click="emit('delete', file)">
                        <Trash2 class="w-4 h-4" />
                        <span>Delete File</span>
                    </BaseButton>
                </div>
            </div>
        </div>
    </BaseModal>
</template>
