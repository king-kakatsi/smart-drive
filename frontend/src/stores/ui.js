import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
  state: () => ({
    isSidebarOpen: true,
    isChatOpen: false,
    theme: 'light'
  }),
  actions: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen
    },
    toggleChat() {
      this.isChatOpen = !this.isChatOpen
    },
    setTheme(theme) {
      this.theme = theme
      if (theme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }
})
