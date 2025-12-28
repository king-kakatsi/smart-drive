import { storeToRefs } from 'pinia'
import { useFilesStore } from '@/stores/files'

export function useFiles() {
  const store = useFilesStore()
  const { 
    files, 
    selectedFile, 
    viewMode, 
    searchQuery, 
    filteredFiles,
    starredFiles,
    isUploading,
    uploadProgress
  } = storeToRefs(store)

  return {
    // State
    files,
    selectedFile,
    viewMode,
    searchQuery,
    filteredFiles,
    starredFiles,
    isUploading,
    uploadProgress,

    // Actions
    setSearchQuery: store.setSearchQuery,
    toggleViewMode: store.toggleViewMode,
    selectFile: store.selectFile,
    toggleStar: store.toggleStar,
    deleteFile: store.deleteFile,
    addFiles: store.addFiles
  }
}
