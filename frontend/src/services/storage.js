export default {
  get: (key) => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : null
    } catch (e) {
      console.error('Error reading from localStorage', e)
      return null
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (e) {
      console.error('Error writing to localStorage', e)
    }
  },
  
  remove: (key) => {
    localStorage.removeItem(key)
  },
  
  clear: () => {
    localStorage.clear()
  }
}
