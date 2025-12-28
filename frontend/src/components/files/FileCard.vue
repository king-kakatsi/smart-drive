<script setup>
import { ref } from 'vue'
import {
    FileText,
    Video,
    Music,
    Image as ImageIcon,
    File,
    MoreVertical,
    Eye,
    MessageSquare,
    Download,
    Trash2,
    Star
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
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

const emit = defineEmits(['preview', 'open-chat', 'delete', 'download', 'toggle-star'])

const isHovered = ref(false)

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
            ? 'p-4 hover:shadow-lg hover:-translate-y-1'
            : 'flex items-center gap-4 p-3 hover:bg-muted/50'
    )" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
        <!-- Grid View -->
        <template v-if="viewMode === 'grid'">
            <div
                class="aspect-video mb-4 rounded-lg overflow-hidden bg-muted/30 flex items-center justify-center relative">
                <component :is="getFileIcon(file.type)"
                    :class="cn('w-12 h-12', getIconColor(file.type).split(' ')[0])" />

                <!-- Hover Actions Overlay -->
                <Transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0"
                    enter-to-class="opacity-100" leave-active-class="transition duration-150 ease-in"
                    leave-from-class="opacity-100" leave-to-class="opacity-0">
                    <div v-if="isHovered" class="absolute inset-0 bg-black/40 flex items-center justify-center gap-2">
                        <button class="p-2 bg-white rounded-lg hover:scale-110 transition-transform" title="Preview"
                            @click="emit('preview', file)">
                            <Eye class="w-4 h-4 text-gray-900" />
                        </button>
                        <button class="p-2 bg-primary rounded-lg hover:scale-110 transition-transform" title="Ask AI"
                            @click="emit('open-chat', file)">
                            <MessageSquare class="w-4 h-4 text-white" />
                        </button>
                    </div>
                </Transition>

                <button class="absolute top-2 right-2 p-1.5 rounded-full bg-white/80 hover:bg-white transition-colors"
                    @click="emit('toggle-star', file)">
                    <Star
                        :class="cn('w-3.5 h-3.5', file.isStarred ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400')" />
                </button>
            </div>

            <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                    <h3 class="text-sm font-medium truncate mb-1">{{ file.name }}</h3>
                    <div class="flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span>{{ file.size }}</span>
                        <span>•</span>
                        <span>{{ file.updatedAt }}</span>
                    </div>
                </div>

                <Dropdown class="shrink-0">
                    <template #trigger>
                        <button class="p-1 hover:bg-muted rounded transition-colors">
                            <MoreVertical class="w-4 h-4 text-muted-foreground" />
                        </button>
                    </template>
                    <DropdownItem @click="emit('download', file)">
                        <Download class="w-4 h-4 mr-2" /> Download
                    </DropdownItem>
                    <DropdownItem class="text-destructive" @click="emit('delete', file)">
                        <Trash2 class="w-4 h-4 mr-2" /> Delete
                    </DropdownItem>
                </Dropdown>
            </div>
        </template>

        <!-- List View -->
        <template v-else>
            <div :class="cn('w-10 h-10 rounded-lg flex items-center justify-center shrink-0', getIconColor(file.type))">
                <component :is="getFileIcon(file.type)" class="w-5 h-5" />
            </div>

            <div class="flex-1 min-w-0">
                <h3 class="text-sm font-medium truncate">{{ file.name }}</h3>
                <p class="text-[10px] text-muted-foreground">{{ file.type.toUpperCase() }} • {{ file.size }}</p>
            </div>

            <div class="hidden md:block text-xs text-muted-foreground px-4">
                {{ file.updatedAt }}
            </div>

            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                    class="p-2 hover:bg-muted rounded-lg transition-colors text-muted-foreground hover:text-foreground"
                    @click="emit('preview', file)">
                    <Eye class="w-4 h-4" />
                </button>
                <button class="p-2 hover:bg-primary/10 rounded-lg transition-colors text-primary"
                    @click="emit('open-chat', file)">
                    <MessageSquare class="w-4 h-4" />
                </button>
            </div>

            <Dropdown>
                <template #trigger>
                    <button class="p-2 hover:bg-muted rounded-lg transition-colors">
                        <MoreVertical class="w-4 h-4 text-muted-foreground" />
                    </button>
                </template>
                <DropdownItem @click="emit('download', file)">
                    <Download class="w-4 h-4 mr-2" /> Download
                </DropdownItem>
                <DropdownItem class="text-destructive" @click="emit('delete', file)">
                    <Trash2 class="w-4 h-4 mr-2" /> Delete
                </DropdownItem>
            </Dropdown>
        </template>
    </div>
</template>
