<script setup>
import { computed } from 'vue'
import {
    LayoutGrid,
    List,
    Upload,
    Plus
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { useFiles } from '@/composables/useFiles'
import BaseButton from '@/components/common/BaseButton.vue'
import FileCard from './FileCard.vue'

const props = defineProps({
    files: {
        type: Array,
        default: () => []
    },
    title: {
        type: String,
        default: 'All Files'
    },
    emptyMessage: {
        type: String,
        default: 'No files found'
    },
    emptyDescription: {
        type: String,
        default: 'Try adjusting your search or upload a new file to get started.'
    },
    onOpenChat: Function,
    onShowUpload: Function,
    onPreviewFile: Function,
    onOpenFolder: Function,
    onOpenFile: Function
})

const { viewMode, setViewMode } = useFiles()
const displayFiles = computed(() => props.files)
</script>

<template>
    <div class="flex flex-col h-full bg-background">
        <!-- Toolbar -->
        <div class="p-4 lg:p-8 border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div class="flex items-center gap-4 flex-1">
                <!-- Search is now handled by global navbar search -->
            </div>

            <div class="flex items-center gap-2">
                <div class="flex items-center bg-muted rounded-lg p-1">
                    <button :class="cn(
                        'p-1.5 rounded-md transition-all',
                        viewMode === 'grid' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'
                    )" @click="setViewMode('grid')">
                        <LayoutGrid class="w-4 h-4" />
                    </button>
                    <button :class="cn(
                        'p-1.5 rounded-md transition-all',
                        viewMode === 'list' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'
                    )" @click="setViewMode('list')">
                        <List class="w-4 h-4" />
                    </button>
                </div>

                <BaseButton class="gap-2" @click="onShowUpload">
                    <Plus class="w-4 h-4" />
                    <span class="hidden sm:inline">Upload</span>
                </BaseButton>
            </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 lg:p-8">
            <div v-if="displayFiles.length > 0">
                <div :class="cn(
                    'grid gap-4',
                    viewMode === 'grid'
                        ? 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4 2xl:grid-cols-5'
                        : 'grid-cols-1'
                )">
                    <FileCard v-for="file in displayFiles" :key="file.id" :file="file" :view-mode="viewMode"
                        @preview="onPreviewFile" @open-chat="onOpenChat" @download="onDownload" @share="onShare" @open-folder="onOpenFolder" @open-file="onOpenFile" />
                </div>
            </div>

            <!-- Empty State -->
            <div v-else class="flex flex-col items-center justify-center h-full text-center py-12">
                <div class="w-24 h-24 rounded-full bg-primary/5 flex items-center justify-center mb-6">
                    <Upload class="w-12 h-12 text-muted-foreground" />
                </div>
                <h3 class="text-lg font-semibold mb-2">{{ emptyMessage }}</h3>
                <p class="text-muted-foreground mb-6 max-w-md">
                    {{ emptyDescription }}
                </p>
                <BaseButton v-if="onShowUpload" size="lg" class="rounded-xl shadow-md" @click="onShowUpload">
                    Upload Your First File
                </BaseButton>
            </div>
        </div>
    </div>
</template>
