import { defineStore } from 'pinia'

export const useFilesStore = defineStore('files', {
  state: () => ({
    files: [
      { id: 1, name: 'Project Proposal.pdf', type: 'pdf', size: '2.4 MB', updatedAt: '2 hours ago', isStarred: true },
      { id: 2, name: 'Product Demo.mp4', type: 'mp4', size: '45.8 MB', updatedAt: '5 hours ago', isStarred: false },
      { id: 3, name: 'Design Assets.zip', type: 'zip', size: '12.1 MB', updatedAt: 'Yesterday', isStarred: false },
      { id: 4, name: 'Meeting Notes.docx', type: 'docx', size: '850 KB', updatedAt: '2 days ago', isStarred: true },
      { id: 5, name: 'Revenue Q4.xlsx', type: 'xlsx', size: '1.2 MB', updatedAt: '3 days ago', isStarred: false },
      { id: 6, name: 'Team Photo.jpg', type: 'jpg', size: '4.2 MB', updatedAt: '1 week ago', isStarred: false },
    ],
    selectedFile: null,
    viewMode: 'grid',
    searchQuery: '',
    isUploading: false,
    uploadProgress: 0
  }),
  
  getters: {
    filteredFiles: (state) => {
      return state.files.filter(file => 
        file.name.toLowerCase().includes(state.searchQuery.toLowerCase())
      )
    },
    starredFiles: (state) => {
      return state.files.filter(file => file.isStarred)
    }
  },
  
  actions: {
    setSearchQuery(query) {
      this.searchQuery = query
    },
    toggleViewMode() {
      this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid'
    },
    selectFile(file) {
      this.selectedFile = file
    },
    toggleStar(fileId) {
      const file = this.files.find(f => f.id === fileId)
      if (file) {
        file.isStarred = !file.isStarred
      }
    },
    deleteFile(fileId) {
      this.files = this.files.filter(f => f.id !== fileId)
    },
    addFiles(newFiles) {
      this.files = [...this.files, ...newFiles]
    }
  }
})
