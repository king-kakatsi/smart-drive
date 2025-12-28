import { defineStore } from 'pinia'
import fileService from '@/services/api/fileService'
import driveService from '@/services/api/driveService'

export const useFilesStore = defineStore('files', {
  state: () => ({
    localFiles: [],
    driveFiles: [],
    selectedFiles: [],
    viewMode: 'grid',
    searchQuery: '',
    isLoading: false,
    error: null,
    isUploading: false,
    uploadProgress: 0,
    storageMetrics: {
      used: 0,
      total: 15 * 1024 * 1024 * 1024, // 15GB default
      limit: 15 * 1024 * 1024 * 1024
    }
  }),
  
  getters: {
    /**
     * Combine local and drive files
     */
    allFiles: (state) => {
      return [...state.localFiles, ...state.driveFiles]
    },

    /**
     * Filter files by search query
     */
    filteredFiles: (state) => {
      const query = state.searchQuery.toLowerCase()
      return state.allFiles.filter(file =>
        file.name?.toLowerCase().includes(query) ||
        file.original_filename?.toLowerCase().includes(query)
      )
    },

    /**
     * Get recent files (last 7 days)
     */
    recentFiles: (state) => {
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)

      return state.allFiles
        .filter(file => {
          const fileDate = new Date(file.modifiedTime || file.updatedAt || file.createdAt)
          return fileDate >= sevenDaysAgo
        })
        .sort((a, b) => new Date(b.modifiedTime || b.updatedAt || b.createdAt) - new Date(a.modifiedTime || a.updatedAt || a.createdAt))
    },

    /**
     * Get starred files
     */
    starredFiles: (state) => {
      return state.allFiles.filter(file => file.isStarred || file.is_starred)
    },

    /**
     * Get trashed files
     */
    trashedFiles: (state) => {
      return state.allFiles.filter(file => file.isTrashed || file.is_trashed)
    },

    /**
     * Get selected file count
     */
    selectedFileCount: (state) => state.selectedFiles.length,

    /**
     * Check if file is selected
     */
    isFileSelected: (state) => (fileId) => {
      return state.selectedFiles.includes(fileId)
    }
  },
  
  actions: {
    /**
     * Fetch all local files
     */
    async fetchAllFiles(folderPath = '/') {
      this.isLoading = true
      this.error = null

      try {
        const response = await fileService.listAllFiles(folderPath)
        this.localFiles = response.files || response || []
        this.isLoading = false
      } catch (error) {
        this.error = error.detail || 'Failed to fetch files'
        this.isLoading = false
      }
    },

    /**
     * Fetch Drive files
     */
    async fetchDriveFiles(pageSize = 100) {
      this.isLoading = true
      this.error = null

      try {
        const response = await driveService.listDriveFiles(pageSize)
        this.driveFiles = response.files || []
        this.isLoading = false
      } catch (error) {
        this.error = error.detail || 'Failed to fetch Drive files'
        this.isLoading = false
      }
    },

    /**
     * Upload file
     */
    async uploadFile(file, folderPath = '/') {
      this.isUploading = true
      this.uploadProgress = 0
      this.error = null

      try {
        const uploadedFile = await fileService.uploadFile(file, folderPath)
        this.localFiles.unshift(uploadedFile)
        this.isUploading = false
        this.uploadProgress = 100
        return uploadedFile
      } catch (error) {
        this.error = error.detail || 'Failed to upload file'
        this.isUploading = false
        this.uploadProgress = 0
        throw error
      }
    },

    /**
     * Delete file
     */
    async deleteFile(fileId) {
      this.error = null

      try {
        await fileService.deleteFile(fileId)
        this.localFiles = this.localFiles.filter(f => f.id !== fileId)
        this.selectedFiles = this.selectedFiles.filter(id => id !== fileId)
      } catch (error) {
        this.error = error.detail || 'Failed to delete file'
        throw error
      }
    },

    /**
     * Move file
     */
    async moveFile(fileId, newPath) {
      this.error = null

      try {
        const updatedFile = await fileService.moveFile(fileId, newPath)
        const index = this.localFiles.findIndex(f => f.id === fileId)
        if (index !== -1) {
          this.localFiles[index] = updatedFile
        }
        return updatedFile
      } catch (error) {
        this.error = error.detail || 'Failed to move file'
        throw error
      }
    },

    /**
     * Create folder
     */
    async createFolder(name, parentPath = '/') {
      this.error = null

      try {
        const folder = await fileService.createFolder(name, parentPath)
        this.localFiles.unshift(folder)
        return folder
      } catch (error) {
        this.error = error.detail || 'Failed to create folder'
        throw error
      }
    },

    /**
     * Search Drive files
     */
    async searchDriveFiles(query) {
      this.isLoading = true
      this.error = null

      try {
        const response = await driveService.searchDriveFiles(query)
        this.driveFiles = response.files || []
        this.isLoading = false
      } catch (error) {
        this.error = error.detail || 'Failed to search Drive files'
        this.isLoading = false
      }
    },

    /**
     * Sync Drive files
     */
    async syncDriveFiles() {
      this.isLoading = true
      this.error = null

      try {
        const response = await driveService.syncDriveFiles()
        // Refresh both local and drive files after sync
        await Promise.all([
          this.fetchAllFiles(),
          this.fetchDriveFiles()
        ])
        this.isLoading = false
        return response
      } catch (error) {
        this.error = error.detail || 'Failed to sync Drive files'
        this.isLoading = false
        throw error
      }
    },

    /**
     * Toggle file selection
     */
    toggleFileSelection(fileId) {
      const index = this.selectedFiles.indexOf(fileId)
      if (index === -1) {
        this.selectedFiles.push(fileId)
      } else {
        this.selectedFiles.splice(index, 1)
      }
    },

    /**
     * Clear all selections
     */
    clearSelection() {
      this.selectedFiles = []
    },

    /**
     * Set search query
     */
    setSearchQuery(query) {
      this.searchQuery = query
    },

    /**
     * Toggle view mode
     */
    toggleViewMode() {
      this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid'
    },
    
    /**
     * Toggle file star status
     */
    async toggleFileStar(fileId) {
      this.error = null

      try {
        // Find the file in localFiles or driveFiles
        let file = this.localFiles.find(f => f.id === fileId)
        let fileType = 'local'

        if (!file) {
          file = this.driveFiles.find(f => f.id === fileId)
          fileType = 'drive'
        }

        if (!file) {
          throw new Error('File not found')
        }

        // Toggle the star status (optimistic update)
        const wasStarred = file.isStarred || file.is_starred
        file.isStarred = !wasStarred
        file.is_starred = !wasStarred

        // TODO: Call backend API when available
        // await fileService.toggleStar(fileId)

      } catch (error) {
        // Revert optimistic update on error
        const file = this.localFiles.find(f => f.id === fileId) || this.driveFiles.find(f => f.id === fileId)
        if (file) {
          file.isStarred = !file.isStarred
          file.is_starred = !file.is_starred
        }

        this.error = error.detail || 'Failed to toggle star status'
        throw error
      }
    },

    /**
     * Fetch storage metrics
     */
    async fetchStorageMetrics() {
      try {
        const response = await driveService.getStorageMetrics()
        if (response && response.quota) {
          this.storageMetrics = {
            used: parseInt(response.quota.usage || 0),
            total: parseInt(response.quota.limit || 15 * 1024 * 1024 * 1024),
            limit: parseInt(response.quota.limit || 15 * 1024 * 1024 * 1024)
          }
        }
      } catch (error) {
        console.error('Failed to fetch storage metrics:', error)
      }
    }
  }
})
