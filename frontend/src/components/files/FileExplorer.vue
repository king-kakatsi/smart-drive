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
    }
})

const emit = defineEmits([
    'open-chat',
    'show-upload',
    'preview-file',
    'open-folder',
    'open-file',
    'open-in-tab',
    'toggle-star',
    'download',
    'share',
    'delete'
])

const { viewMode, setViewMode } = useFiles()
const displayFiles = computed(() => props.files)
</script>

<template>
    <div class="flex flex-col h-full bg-background/50 overflow-hidden">
        <!-- Persistent Glass Header / Toolbar -->
        <div
            class="sticky top-0 z-40 backdrop-blur-xl bg-white/70 dark:bg-slate-900/70 border-b border-white/20 dark:border-white/5 p-4 lg:px-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
            <div class="flex items-center gap-3">
                <h2 class="text-xl font-extrabold tracking-tight text-foreground/90">{{ title }}</h2>
                <div v-if="files.length > 0"
                    class="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider">
                    {{ files.length }} items
                </div>
            </div>

            <div class="flex items-center gap-3">
                <!-- View Mode Switcher -->
                <div class="flex items-center bg-muted/50 rounded-xl p-1 border border-border/50">
                    <button :class="cn(
                        'p-2 rounded-lg transition-all duration-300',
                        viewMode === 'grid' ? 'bg-background shadow-md text-primary' : 'text-muted-foreground hover:text-foreground'
                    )" @click="setViewMode('grid')">
                        <LayoutGrid class="w-4 h-4" />
                    </button>
                    <button :class="cn(
                        'p-2 rounded-lg transition-all duration-300',
                        viewMode === 'list' ? 'bg-background shadow-md text-primary' : 'text-muted-foreground hover:text-foreground'
                    )" @click="setViewMode('list')">
                        <List class="w-4 h-4" />
                    </button>
                </div>

                <BaseButton
                    class="gap-2 rounded-xl px-5 shadow-lg shadow-primary/20 transition-all hover:scale-[1.02] active:scale-95"
                    @click="$emit('show-upload')">
                    <Plus class="w-4 h-4" />
                    <span class="hidden sm:inline font-bold">Upload</span>
                </BaseButton>
            </div>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-y-auto p-4 lg:p-8 custom-scrollbar">
            <div v-if="displayFiles.length > 0">
                <div :class="cn(
                    'grid gap-6',
                    viewMode === 'grid'
                        ? 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6'
                        : 'grid-cols-1'
                )">
                    <FileCard v-for="file in displayFiles" :key="file.id" :file="file" :view-mode="viewMode"
                        @preview="$emit('preview-file', $event)" @open-chat="$emit('open-chat', $event)"
                        @download="$emit('download', $event)" @share="$emit('share', $event)"
                        @delete="$emit('delete', $event)" @toggle-star="$emit('toggle-star', $event)"
                        @open-folder="$emit('open-folder', $event)" @open-file="$emit('open-file', $event)"
                        @open-in-tab="$emit('open-in-tab', $event)" />
                </div>
            </div>

            <!-- Enhanced Empty State -->
            <div v-else class="flex flex-col items-center justify-center min-h-[60vh] text-center p-8">
                <div class="relative mb-8 text-primary">
                    <div
                        class="absolute inset-0 bg-primary/20 blur-3xl rounded-full scale-150 transform -translate-y-4" />
                    <Upload class="w-16 h-16 relative z-10 opacity-40 animate-bounce" />
                </div>

                <h3 class="text-2xl font-black mb-2 tracking-tight text-foreground">{{ emptyMessage }}</h3>
                <p class="text-muted-foreground mb-8 max-w-sm font-medium leading-relaxed">
                    {{ emptyDescription }}
                </p>

                <BaseButton size="lg"
                    class="rounded-2xl px-10 py-6 text-base shadow-xl shadow-primary/30 transition-all hover:-translate-y-1"
                    @click="$emit('show-upload')">
                    Start Uploading
                </BaseButton>
            </div>
        </div>
    </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: var(--muted);
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: var(--muted-foreground);
}
</style>
