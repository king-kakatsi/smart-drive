<script setup>
import { ref, computed } from 'vue'
import {
    FileText,
    Video,
    Music,
    Image as ImageIcon,
    File,
    Folder,
    MoreVertical,
    Eye,
    MessageSquare,
    Download,
    Trash2,
    Share2,
    Star,
    ExternalLink
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { useFilesStore } from '@/stores/files'
import BaseBadge from '@/components/common/BaseBadge.vue'
import Dropdown, { DropdownItem } from '@/components/common/Dropdown.vue'

const props = defineProps({
    file: {
        type: Object,
        required: true
    },
    viewMode: {
        type: String,
        default: 'grid'
    }
})

const emit = defineEmits(['preview', 'open-chat', 'delete', 'download', 'share', 'toggle-star', 'open-folder', 'open-file', 'open-in-tab'])

const isHovered = ref(false)
const filesStore = useFilesStore()

const isFileStarred = computed(() => {
    return filesStore.starredFileIds.includes(props.file.id)
})

const displayName = computed(() => {
    // Handle multiple possible field names for filename from different sources
    return props.file.name ||
        props.file.original_filename ||
        props.file.filename ||
        props.file.title ||
        'Unnamed File'
})

const isFolder = computed(() => {
    return props.file.mimeType === 'application/vnd.google-apps.folder' ||
        props.file.type === 'folder' ||
        props.file.file_type === 'folder'
})


const getFileIcon = (file) => {
    // Handle both file.type and file.mimeType
    // Check for Google Drive folder first
    if (file.mimeType === 'application/vnd.google-apps.folder' ||
        file.type === 'folder' ||
        file.file_type === 'folder') {
        return Folder
    }

    const type = file.type || file.mimeType?.split('/').pop() || 'file'
    switch (type.toLowerCase()) {
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

const handleCardClick = (event) => {

    if (isFolder.value) {
        // Folders are always clickable for navigation
        emit('open-folder', props.file)
        return
    }

    // For files, don't open if clicking on buttons, dropdowns, or their children
    const target = event.target
    const isButton = target.tagName === 'BUTTON' || target.closest('button')
    const isDropdown = target.closest('[class*="dropdown"]') || target.closest('.relative')


    if (!isButton && !isDropdown) {
        emit('open-file', props.file)
    }
}

const getIconColor = (file) => {
    // Check for Google Drive folder first
    if (file.mimeType === 'application/vnd.google-apps.folder' ||
        file.type === 'folder' ||
        file.file_type === 'folder') {
        return 'text-[var(--file-folder)] bg-[var(--file-folder)]/10'
    }

    const type = file.type || file.mimeType?.split('/').pop() || 'file'
    switch (type.toLowerCase()) {
        case 'pdf': return 'text-[var(--file-pdf)] bg-[var(--file-pdf)]/10'
        case 'doc':
        case 'docx': return 'text-[var(--file-word)] bg-[var(--file-word)]/10'
        case 'mp4':
        case 'mov':
        case 'video': return 'text-[var(--file-video)] bg-[var(--file-video)]/10'
        case 'mp3':
        case 'wav':
        case 'audio': return 'text-[var(--file-audio)] bg-[var(--file-audio)]/10'
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
        case 'image': return 'text-[var(--file-image)] bg-[var(--file-image)]/10'
        default: return 'text-primary bg-primary/10'
    }
}
</script>

<template>
    <div :class="cn(
        'group relative rounded-2xl border transition-all duration-300',
        'backdrop-blur-sm bg-white/40 dark:bg-slate-900/40 border-white/20 dark:border-white/5',
        viewMode === 'grid'
            ? 'p-4 hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-1.5'
            : 'flex items-center gap-4 p-3 hover:bg-muted/40',
        isFileStarred && 'border-primary/20 bg-primary/[0.02]',
        isFolder ? 'cursor-pointer' : ''
    )" @click="handleCardClick" @mouseenter="isHovered = true" @mouseleave="isHovered = false">

        <!-- Grid View -->
        <template v-if="viewMode === 'grid'">
            <div class="relative mb-4">
                <!-- Icon/Thumbnail Container -->
                <div :class="cn(
                    'aspect-[4/3] rounded-xl flex items-center justify-center transition-all duration-500',
                    getIconColor(file),
                    'group-hover:scale-105 group-hover:rotate-1 shadow-sm relative overflow-hidden'
                )">
                    <component :is="getFileIcon(file)"
                        :class="cn('w-12 h-12 relative z-10', getIconColor(file).split(' ')[0])" />
                </div>

                <!-- Star Toggle (Overlay) -->
                <button v-if="!isFolder"
                    class="absolute top-2 right-2 p-1.5 rounded-full bg-white/20 backdrop-blur-md border border-white/30 opacity-0 group-hover:opacity-100 transition-all hover:bg-white/40 z-30"
                    @click.stop="emit('toggle-star', file)">
                    <Star
                        :class="cn('w-3.5 h-3.5 transition-colors', isFileStarred ? 'fill-yellow-400 text-yellow-400' : 'text-slate-400')" />
                </button>
            </div>

            <!-- File Info -->
            <div class="space-y-1">
                <h3 class="text-sm font-semibold truncate group-hover:text-primary transition-colors">
                    {{ displayName }}
                </h3>

                <div
                    class="flex items-center text-[10px] text-muted-foreground font-medium uppercase tracking-wider opacity-80">
                    <span>{{ file.size || 'Size N/A' }}</span>
                    <span class="mx-1.5 text-muted-foreground/30">•</span>
                    <span>{{ file.updatedAt || new Date(file.created_at).toLocaleDateString() }}</span>
                </div>
            </div>

            <!-- Floating Actions Bar (Subtle) -->
            <div :class="cn(
                'absolute -bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-1 p-1 rounded-full',
                'bg-slate-100/95 dark:bg-slate-800/95 backdrop-blur-xl shadow-xl border border-white/20 transition-all duration-300',
                'opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 pointer-events-none group-hover:pointer-events-auto z-50'
            )">
                <button v-if="!isFolder"
                    class="p-2 rounded-full hover:bg-primary/10 text-muted-foreground hover:text-primary transition-all"
                    @click.stop="emit('preview', file)" title="Preview">
                    <Eye class="w-4 h-4" />
                </button>
                <button v-if="!isFolder"
                    class="p-2 rounded-full hover:bg-secondary/10 text-muted-foreground hover:text-secondary transition-all"
                    @click.stop="emit('open-chat', file)" title="AI Chat">
                    <MessageSquare class="w-4 h-4" />
                </button>
                <button v-if="!isFolder"
                    class="p-2 rounded-full hover:bg-green-500/10 text-muted-foreground hover:text-green-600 transition-all"
                    @click.stop="emit('open-in-tab', file)" title="Open in New Tab">
                    <ExternalLink class="w-4 h-4" />
                </button>
                <!-- Dropdown commented out as requested -->
                <!-- <Dropdown v-if="!isFolder">
                    <template #trigger>
                        <button class="p-2 rounded-full hover:bg-muted transition-all">
                            <MoreVertical class="w-4 h-4 text-muted-foreground" />
                        </button>
                    </template>
<DropdownItem @click.stop="emit('share', file)">
    <Share2 class="w-4 h-4 mr-2" /> Share
</DropdownItem>
<DropdownItem @click.stop="emit('download', file)">
    <Download class="w-4 h-4 mr-2" /> Download
</DropdownItem>
<DropdownItem class="text-destructive" @click.stop="emit('delete', file)">
    <Trash2 class="w-4 h-4 mr-2" /> Delete
</DropdownItem>
</Dropdown> -->
            </div>
        </template>

        <!-- List View -->
        <template v-else>
            <div
                :class="cn('w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm transition-transform group-hover:scale-105', getIconColor(file))">
                <component :is="getFileIcon(file)" :class="cn('w-5 h-5', getIconColor(file).split(' ')[0])" />
            </div>

            <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold truncate group-hover:text-primary transition-colors">{{ displayName }}
                </h3>
                <div
                    class="flex items-center gap-2 text-[10px] font-medium text-muted-foreground uppercase tracking-widest opacity-60">
                    <span>{{ (file.type || file.mimeType?.split('/').pop() || 'FILE') }}</span>
                    <span>•</span>
                    <span>{{ file.size }}</span>
                </div>
            </div>

            <div class="hidden md:block text-[11px] text-muted-foreground font-medium px-4">
                {{ file.updatedAt || new Date(file.created_at).toLocaleDateString() }}
            </div>

            <div
                class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all translate-x-1 group-hover:translate-x-0">
                <template v-if="!isFolder">
                    <button
                        class="p-2 hover:bg-primary/10 rounded-xl text-muted-foreground hover:text-primary transition-all"
                        @click.stop="emit('preview', file)">
                        <Eye class="w-4 h-4" />
                    </button>
                    <button
                        class="p-2 hover:bg-secondary/10 rounded-xl text-muted-foreground hover:text-secondary transition-all"
                        @click.stop="emit('open-chat', file)">
                        <MessageSquare class="w-4 h-4" />
                    </button>
                </template>

                <!-- Dropdown commented out as requested -->
                <!-- <Dropdown>
                    <template #trigger>
                        <button class="p-2 hover:bg-muted rounded-xl transition-all">
                            <MoreVertical class="w-4 h-4 text-muted-foreground" />
                        </button>
                    </template>
                    <DropdownItem v-if="!isFolder" @click.stop="emit('share', file)">
                        <Share2 class="w-4 h-4 mr-2" /> Share
                    </DropdownItem>
                    <DropdownItem v-if="!isFolder" @click.stop="emit('download', file)">
                        <Download class="w-4 h-4 mr-2" /> Download
                    </DropdownItem>
                    <DropdownItem class="text-destructive" @click.stop="emit('delete', file)">
                        <Trash2 class="w-4 h-4 mr-2" /> Delete
                    </DropdownItem>
                </Dropdown> -->
            </div>
        </template>
    </div>
</template>
