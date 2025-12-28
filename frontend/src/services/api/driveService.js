/**
 * Drive Service
 * Handles Google Drive API operations
 */
import apiClient from './apiClient'

class DriveService {
  /**
   * List files from Google Drive
   */
  async listDriveFiles(pageSize = 100, pageToken = null) {
    let endpoint = `/api/v1/drive/files?page_size=${pageSize}`
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
   * Get storage and quota metrics
   */
  async getStorageMetrics() {
    return await apiClient.get('/api/v1/drive/metrics')
  }
}

// Export singleton instance
export default new DriveService()
