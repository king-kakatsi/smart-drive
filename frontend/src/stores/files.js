import { defineStore } from 'pinia'
import fileService from '@/services/api/fileService'
import driveService from '@/services/api/driveService'

export const useFilesStore = defineStore('files', {
  state: () => ({
    localFiles: [],
    driveFiles: [],
    selectedFiles: [],
    starredFileIds: [],
    viewMode: 'grid',
    searchQuery: '',
    isLoading: false,
    error: null,
    isUploading: false,
    uploadProgress: 0,
    isDataLoaded: false,
    // Folder navigation state
    currentFolderPath: '/',
    folderHistory: ['/'],
    folderContents: [],
    isNavigating: false,
    folderIdMap: JSON.parse(localStorage.getItem('folderIdMap') || '{}'), // Maps folder paths to Drive folder IDs
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
      const fileMap = new Map()
      
      // 1. Add all local records first
      state.localFiles.forEach(localFile => {
        // Use drive_file_id as key if it exists, otherwise use local ID
        const key = localFile.drive_file_id || `local_${localFile.id}`
        fileMap.set(key, { 
          ...localFile, 
          name: localFile.original_filename || localFile.filename || localFile.name,
          isLocal: true 
        })
      })
      
      // 2. Merge in Drive records
      state.driveFiles.forEach(driveFile => {
        const key = driveFile.id
        if (fileMap.has(key)) {
          const localRecord = fileMap.get(key)
          fileMap.set(key, {
            ...localRecord, // Local intelligence (processed, file_type, path)
            ...driveFile,   // Priority: Drive richness (Name, webViewLink, thumbnailLink, size)
            id: driveFile.id, // Ensure primary ID is the Drive string ID
            local_id: localRecord.id, // Keep numeric ID for backend operations
            drive_file_id: driveFile.id,
            isSynced: true,
            isLocal: true
          })
        } else {
          // Drive file not in local database yet
          fileMap.set(key, { 
            ...driveFile, 
            id: driveFile.id, 
            drive_file_id: driveFile.id,
            isDriveOnly: true 
          })
        }
      })
      
      return Array.from(fileMap.values())
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
      return state.allFiles.filter(file => state.starredFileIds.includes(file.id))
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
        // Find the file to determine if it's local or from Drive
        let file = this.localFiles.find(f => f.id === fileId)
        let isDriveFile = false

        if (!file) {
          file = this.driveFiles.find(f => f.id === fileId)
          isDriveFile = true
        }

        if (!file) {
          throw new Error('File not found')
        }

        // Update appropriate arrays
        if (file.drive_file_id) {
          // Google Drive file (synced or standalone)
          await driveService.deleteDriveFile(file.drive_file_id)
          this.driveFiles = this.driveFiles.filter(f => f.id !== file.drive_file_id)
          // If it was also in localFiles, it should be filtered out from folderContents later
          this.localFiles = this.localFiles.filter(f => f.drive_file_id !== file.drive_file_id)
        } else {
          // Local only file
          await fileService.deleteFile(fileId)
          this.localFiles = this.localFiles.filter(f => f.id !== fileId)
        }

        // Fix: Also filter folderContents to update the UI reactively
        this.folderContents = this.folderContents.filter(f => f.id !== fileId)

        // Remove from selected files
        this.selectedFiles = this.selectedFiles.filter(id => id !== fileId)

        // Refresh storage metrics after deletion
        this.fetchStorageMetrics().catch(err => console.warn('Failed to refresh metrics:', err))
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
     * Helper: Save starred file IDs to localStorage
     */
    saveStarredToLocalStorage() {
      localStorage.setItem('starred_files', JSON.stringify(this.starredFileIds))
    },

    /**
     * Helper: Load starred file IDs from localStorage
     */
    loadStarredFromLocalStorage() {
      const stored = localStorage.getItem('starred_files')
      this.starredFileIds = stored ? JSON.parse(stored) : []
    },

    /**
     * Toggle file star status
     */
    async toggleFileStar(fileId) {
      this.error = null

      try {
        // Find the file in localFiles or driveFiles
        let file = this.localFiles.find(f => f.id === fileId)

        if (!file) {
          file = this.driveFiles.find(f => f.id === fileId)
        }

        if (!file) {
          throw new Error('File not found')
        }

        // Toggle the star status in our local array
        const index = this.starredFileIds.indexOf(fileId)
        if (index > -1) {
          this.starredFileIds.splice(index, 1) // Unstar
        } else {
          this.starredFileIds.push(fileId) // Star
        }

        // Persist to localStorage
        this.saveStarredToLocalStorage()

        // TODO: Call backend API when available
        // await fileService.toggleStar(fileId)

      } catch (error) {
        // Revert optimistic update on error
        const index = this.starredFileIds.indexOf(fileId)
        if (index > -1) {
          this.starredFileIds.splice(index, 1)
        } else {
          this.starredFileIds.push(fileId)
        }

        this.error = error.detail || 'Failed to toggle star status'
        throw error
      }
    },

    /**
     * Initialize store (load persisted data)
     */
    initializeStore() {
      this.loadStarredFromLocalStorage()

      // Load view mode preference
      const savedViewMode = localStorage.getItem('file_view_mode')
      if (savedViewMode && (savedViewMode === 'grid' || savedViewMode === 'list')) {
        this.viewMode = savedViewMode
      }
    },

    /**
     * Set view mode with persistence
     */
    setViewMode(mode) {
      if (mode === 'grid' || mode === 'list') {
        this.viewMode = mode
        localStorage.setItem('file_view_mode', mode)
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
    },

    /**
     * Navigate to a specific folder
     */
    async navigateToFolder(folderPath, folderId = null) {
      this.isNavigating = true
      this.error = null

      try {
        this.currentFolderPath = folderPath

        // Update folder history
        const historyIndex = this.folderHistory.indexOf(folderPath)
        if (historyIndex >= 0) {
          // If path already exists in history, truncate to that point
          this.folderHistory = this.folderHistory.slice(0, historyIndex + 1)
        } else {
          // Add new path to history
          this.folderHistory.push(folderPath)
        }

        // Store folder ID mapping for Google Drive and persist it
        if (folderId) {
          this.folderIdMap[folderPath] = folderId
          localStorage.setItem('folderIdMap', JSON.stringify(this.folderIdMap))
        }

        await this.fetchFolderContents(folderPath)
      } catch (error) {
        this.error = error.message || 'Failed to navigate to folder'
        throw error
      } finally {
        this.isNavigating = false
      }
    },

    /**
     * Navigate up one level
     */
    async navigateUp() {
      if (this.folderHistory.length > 1) {
        this.folderHistory.pop()
        const parentPath = this.folderHistory[this.folderHistory.length - 1]
        await this.navigateToFolder(parentPath)
      }
    },

    /**
     * Fetch contents of a specific folder
     */
    async fetchFolderContents(folderPath) {
      this.isLoading = true
      this.error = null

      try {
        if (folderPath === '/') {
          // Root folder - fetch all files
          await Promise.all([
            this.fetchAllFiles('/'),
            this.fetchDriveFiles()
          ])
          this.folderContents = this.allFiles
        } else {
          // Subfolder - fetch specific folder contents
          const [localFiles, driveFiles] = await Promise.all([
            fileService.listAllFiles(folderPath),
            this.fetchDriveFolderContents(folderPath)
          ])
          this.folderContents = [...localFiles, ...driveFiles]
        }
      } catch (error) {
        this.error = error.message || 'Failed to fetch folder contents'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Fetch Google Drive folder contents
     */
    async fetchDriveFolderContents(folderPath) {
      if (folderPath === '/') {
        // Root level Drive files
        const response = await driveService.listDriveFiles()
        return response.files || []
      }

      // Find the Drive folder ID for this path
      const folderId = this.folderIdMap[folderPath]
      if (!folderId) {
        return []
      }

      // For Drive subfolders, we need to filter files by parent
      // This is a simplified approach - in a real implementation,
      // you might want to cache folder hierarchies
      try {
        const response = await driveService.listDriveFiles(1000, null, folderId)
        return response.files || []
      } catch (error) {
        console.error('Failed to fetch Drive folder contents:', error)
        return []
      }
    }
  }
})
