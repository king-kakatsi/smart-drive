/**
 * Drive Service
 * Handles Google Drive API operations
 */
import apiClient from './apiClient'

class DriveService {
  /**
   * List files from Google Drive
   */
  async listDriveFiles(pageSize = 100, pageToken = null, folderId = 'root') {
    let endpoint = `/api/v1/drive/files?page_size=${pageSize}&folder_id=${folderId}`
    if (pageToken) {
      endpoint += `&page_token=${pageToken}`
    }
    return await apiClient.get(endpoint)
  }

  /**
   * Get Drive file metadata
   */
  async getDriveFileMetadata(fileId) {
    return await apiClient.get(`/api/v1/drive/files/${fileId}`)
  }

  /**
   * Search Drive files
   */
  async searchDriveFiles(query, pageSize = 50) {
    return await apiClient.get(`/api/v1/drive/search?query=${encodeURIComponent(query)}&page_size=${pageSize}`)
  }

  /**
   * Sync Drive files
   */
  async syncDriveFiles() {
    return await apiClient.post('/api/v1/drive/sync')
  }

  /**
   * Download Drive file
   */
  async downloadDriveFile(fileId) {
    const url = `${apiClient.baseUrl}/api/v1/drive/files/${fileId}/download`
    const headers = apiClient.getAuthorizationHeader()
    
    const response = await fetch(url, { headers })
    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.statusText}`)
    }
    
    return await response.blob()
  }

  /**
   * Upload file to Google Drive
   */
  async uploadFileToDrive(file, folderId = null, folderPath = '/') {

    const formData = new FormData()
    formData.append('file', file)
    if (folderId) {
      formData.append('folder_id', folderId)
    }
    formData.append('folder_path', folderPath)

    try {
      const response = await apiClient.uploadFile('/api/v1/drive/upload', formData)
      return response
    } catch (error) {
      throw error
    }
  }

  /**
   * Delete (trash) a Drive file
   */
  async deleteDriveFile(fileId) {
    return await apiClient.delete(`/api/v1/drive/files/${fileId}`)
  }

  /**
   * Get storage and quota metrics
   */
  async getStorageMetrics() {
    return await apiClient.get('/api/v1/drive/metrics')
  }
}

// Export singleton instance
export default new DriveService()
