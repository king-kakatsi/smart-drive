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

const displayName = computed(() => {
    // Handle multiple possible field names for filename
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

// Debug: Log file object structure
console.log('FileCard file object:', {
    id: props.file.id,
    name: props.file.name,
    filename: props.file.filename,
    original_filename: props.file.original_filename,
    title: props.file.title,
    mimeType: props.file.mimeType,
    type: props.file.type,
    file_type: props.file.file_type
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
    console.log('FileCard clicked:', {
        name: props.file.name,
        mimeType: props.file.mimeType,
        type: props.file.type,
        file_type: props.file.file_type,
        isFolder: isFolder.value
    })

    if (isFolder.value) {
        // Folders are always clickable for navigation
        console.log('Opening as folder:', props.file.name)
        emit('open-folder', props.file)
        return
    }

    // For files, don't open if clicking on buttons, dropdowns, or their children
    const target = event.target
    const isButton = target.tagName === 'BUTTON' || target.closest('button')
    const isDropdown = target.closest('[class*="dropdown"]') || target.closest('.relative')

    console.log('File click details:', {
        target: target.tagName,
        isButton,
        isDropdown,
        willOpen: !isButton && !isDropdown
    })

    if (!isButton && !isDropdown) {
        console.log('Opening as file:', props.file.name)
        emit('open-file', props.file)
    }
}

const getIconColor = (file) => {
    // Check for Google Drive folder first
    if (file.mimeType === 'application/vnd.google-apps.folder' ||
        file.type === 'folder' ||
        file.file_type === 'folder') {
        return 'text-yellow-600 bg-yellow-50'
    }

    const type = file.type || file.mimeType?.split('/').pop() || 'file'
    switch (type.toLowerCase()) {
        case 'pdf': return 'text-red-500 bg-red-50'
        case 'doc':
        case 'docx': return 'text-blue-500 bg-blue-50'
        case 'mp4':
        case 'mov': return 'text-purple-500 bg-purple-50'
        case 'mp3': return 'text-pink-500 bg-pink-50'
        case 'jpg':
        case 'png': return 'text-orange-500 bg-orange-50'
        default: return 'text-gray-500 bg-gray-50'
    }
}
</script>

<template>
    <div :class="cn(
        'group relative bg-card rounded-xl border border-border transition-all duration-200',
        viewMode === 'grid'
            ? 'p-4 hover:shadow-lg hover:-translate-y-1 hover:z-[10000]'
            : 'flex items-center gap-4 p-3 hover:bg-muted/50',
        isFolder ? 'cursor-pointer' : ''
    )" @mouseenter="isHovered = true" @mouseleave="isHovered = false" @click="handleCardClick">
        <!-- Grid View -->
        <template v-if="viewMode === 'grid'">
            <div
                class="aspect-video mb-4 rounded-lg overflow-hidden bg-muted/30 flex items-center justify-center relative">
                <component :is="getFileIcon(file)"
                    :class="cn('w-12 h-12', getIconColor(file).split(' ')[0])" />

                <!-- Hover Actions Overlay (only for files, not folders) -->
                <Transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0"
                    enter-to-class="opacity-100" leave-active-class="transition duration-150 ease-in"
                    leave-from-class="opacity-100" leave-to-class="opacity-0">
                    <div v-if="isHovered && !isFolder" class="absolute inset-0 bg-black/40 flex items-center justify-center gap-2">
                        <button class="p-2 bg-white rounded-lg hover:scale-110 transition-transform" title="Preview"
                            @click.stop="emit('preview', file)">
                            <Eye class="w-4 h-4 text-gray-900" />
                        </button>
                        <button class="p-2 bg-primary rounded-lg hover:scale-110 transition-transform" title="Ask AI"
                            @click.stop="emit('open-chat', file)">
                            <MessageSquare class="w-4 h-4 text-white" />
                        </button>
                        <button class="p-2 bg-green-500 rounded-lg hover:scale-110 transition-transform" title="Open in New Tab"
                            @click.stop="emit('open-in-tab', file)">
                            <ExternalLink class="w-4 h-4 text-white" />
                        </button>
                    </div>
                </Transition>

                <!-- Star button (only for files, not folders) -->
                <button v-if="!isFolder" class="absolute top-2 right-2 p-1.5 rounded-full bg-white/80 hover:bg-white transition-colors"
                    @click.stop="emit('toggle-star', file)">
                    <Star
                        :class="cn('w-3.5 h-3.5', isFileStarred ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400')" />
                </button>
            </div>

            <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                    <h3 class="text-sm font-medium truncate mb-1">{{ displayName }}</h3>
                    <div class="flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span>{{ file.size }}</span>
                        <span>•</span>
                        <span>{{ file.updatedAt }}</span>
                    </div>
                </div>

                <Dropdown v-if="!isFolder" class="shrink-0 bg-gray-100">
                    <template #trigger>
                        <button class="p-1 hover:bg-muted rounded transition-colors">
                            <MoreVertical class="w-4 h-4 text-muted-foreground" />
                        </button>
                    </template>
                    <DropdownItem @click.stop="emit('download', file)">
                        <Download class="w-4 h-4 mr-2" /> Download
                    </DropdownItem>
                    <DropdownItem class="text-destructive" @click.stop="emit('delete', file)">
                        <Trash2 class="w-4 h-4 mr-2" /> Delete
                    </DropdownItem>
                </Dropdown>
            </div>
        </template>

        <!-- List View -->
        <template v-else>
            <div :class="cn('w-10 h-10 rounded-lg flex items-center justify-center shrink-0', getIconColor(file))">
                <component :is="getFileIcon(file)" class="w-5 h-5" />
            </div>

            <div class="flex-1 min-w-0">
                <h3 class="text-sm font-medium truncate">{{ displayName }}</h3>
                <p class="text-[10px] text-muted-foreground">{{ (file.type || file.mimeType?.split('/').pop() || 'FILE').toUpperCase() }} • {{ file.size }}</p>
            </div>

            <div class="hidden md:block text-xs text-muted-foreground px-4">
                {{ file.updatedAt }}
            </div>

            <!-- Hover actions (only for files, not folders) -->
            <div v-if="!isFolder" class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                    class="p-2 hover:bg-muted rounded-lg transition-colors text-muted-foreground hover:text-foreground"
                    @click.stop="emit('preview', file)">
                    <Eye class="w-4 h-4" />
                </button>
                <button class="p-2 hover:bg-primary/10 rounded-lg transition-colors text-primary"
                    @click.stop="emit('open-chat', file)">
                    <MessageSquare class="w-4 h-4" />
                </button>
                <button class="p-2 hover:bg-green-500/10 rounded-lg transition-colors text-green-600 hover:text-green-700"
                    @click.stop="emit('open-in-tab', file)">
                    <ExternalLink class="w-4 h-4" />
                </button>
            </div>

            <!-- Dropdown menu (only for files, not folders) -->
            <Dropdown v-if="!isFolder">
                <template #trigger>
                    <button class="p-2 hover:bg-muted rounded-lg transition-colors">
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
            </Dropdown>
        </template>
    </div>
</template>
