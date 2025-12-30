/**
 * File Service
 * Handles local file operations
 */
import apiClient from './apiClient'

class FileService {
  /**
   * Upload file
   */
  async uploadFile(file, folderPath = '/') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('folder_path', folderPath)
    
    return await apiClient.uploadFile('/api/v1/files/upload', formData)
  }

  /**
   * List all files
   */
  async listAllFiles(folderPath = '/') {
    return await apiClient.get(`/api/v1/files?folder_path=${encodeURIComponent(folderPath)}`)
  }

  /**
   * Get file by ID
   */
  async getFileById(fileId) {
    return await apiClient.get(`/api/v1/files/${fileId}`)
  }

  /**
   * Delete file
   */
  async deleteFile(fileId) {
    return await apiClient.delete(`/api/v1/files/${fileId}`)
  }

  /**
   * Move file
   */
  async moveFile(fileId, newPath) {
    return await apiClient.put(`/api/v1/files/${fileId}/move`, { new_path: newPath })
  }

  /**
   * Create folder
   */
  async createFolder(name, parentPath = '/') {
    return await apiClient.post('/api/v1/files/folders', {
      name,
      parent_path: parentPath
    })
  }

  /**
   * Download file
   */
  async downloadFile(fileId) {
    const url = `${apiClient.baseUrl}/api/v1/files/${fileId}/download`
    const headers = apiClient.getAuthorizationHeader()
    
    const response = await fetch(url, { headers })
    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.statusText}`)
    }
    
    return await response.blob()
  }
}

// Export singleton instance
export default new FileService()
