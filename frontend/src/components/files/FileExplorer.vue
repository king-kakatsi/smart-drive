<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import {
    Search,
    LayoutGrid,
    List,
    Filter,
    Upload,
    ArrowUpDown,
    Plus
} from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { useFiles } from '@/composables/useFiles'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import FileCard from './FileCard.vue'
import Dropdown, { DropdownItem } from '@/components/common/Dropdown.vue'

const props = defineProps({
    onOpenChat: Function,
    onShowUpload: Function,
    onPreviewFile: Function
})

const filesStore = useFilesStore()
const { viewMode, searchQuery, filteredFiles } = storeToRefs(filesStore)

const sortBy = ref('name')
</script>

<template>
    <div class="flex flex-col h-full bg-background">
        <!-- Toolbar -->
        <div class="p-4 lg:p-8 border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div class="flex items-center gap-4 flex-1">
                <div class="relative w-full max-w-md">
                    <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <BaseInput v-model="searchQuery" placeholder="Search files or ask AI..."
                        class="pl-10 bg-muted/30 border-none" />
                </div>
                <BaseButton variant="outline" size="icon" class="shrink-0">
                    <Filter class="w-4 h-4" />
                </BaseButton>
            </div>

            <div class="flex items-center gap-2">
                <div class="flex items-center bg-muted rounded-lg p-1">
                    <button :class="cn(
                        'p-1.5 rounded-md transition-all',
                        viewMode === 'grid' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'
                    )" @click="viewMode = 'grid'">
                        <LayoutGrid class="w-4 h-4" />
                    </button>
                    <button :class="cn(
                        'p-1.5 rounded-md transition-all',
                        viewMode === 'list' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'
                    )" @click="viewMode = 'list'">
                        <List class="w-4 h-4" />
                    </button>
                </div>

                <Dropdown>
                    <template #trigger>
                        <BaseButton variant="outline" class="gap-2">
                            <ArrowUpDown class="w-4 h-4" />
                            <span class="hidden sm:inline">Sort</span>
                        </BaseButton>
                    </template>
                    <DropdownItem @click="sortBy = 'name'">Name</DropdownItem>
                    <DropdownItem @click="sortBy = 'date'">Date Modified</DropdownItem>
                    <DropdownItem @click="sortBy = 'size'">Size</DropdownItem>
                </Dropdown>

                <BaseButton class="gap-2" @click="onShowUpload">
                    <Plus class="w-4 h-4" />
                    <span class="hidden sm:inline">Upload</span>
                </BaseButton>
            </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 lg:p-8">
            <div v-if="filteredFiles.length > 0">
                <div :class="cn(
                    'grid gap-4',
                    viewMode === 'grid'
                        ? 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'
                        : 'grid-cols-1'
                )">
                    <FileCard v-for="file in filteredFiles" :key="file.id" :file="file" :view-mode="viewMode"
                        @preview="onPreviewFile" @open-chat="onOpenChat" />
                </div>
            </div>

            <!-- Empty State -->
            <div v-else class="flex flex-col items-center justify-center h-full text-center py-12">
                <div class="w-24 h-24 rounded-full bg-primary/5 flex items-center justify-center mb-6">
                    <Upload class="w-12 h-12 text-muted-foreground" />
                </div>
                <h3 class="text-lg font-semibold mb-2">No files found</h3>
                <p class="text-muted-foreground mb-6 max-w-md">
                    Try adjusting your search or upload a new file to get started.
                </p>
                <BaseButton size="lg" class="rounded-xl shadow-md" @click="onShowUpload">
                    Upload Your First File
                </BaseButton>
            </div>
        </div>
    </div>
</template>
