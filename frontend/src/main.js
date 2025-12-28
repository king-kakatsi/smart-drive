import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Simple route for testing
const routes = [
  { path: '/', component: { template: '<div class="p-8"><h1 class="text-2xl font-bold text-blue-600">Smart-Drive Frontend Working!</h1><p class="mt-4 text-gray-600">Vue.js + Vite development server is running correctly.</p></div>' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Create and mount app
const app = createApp(App)
app.use(router)
app.mount('#app')


