import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/files',
    name: 'FileExplorer',
    component: () => import('@/views/FileExplorer.vue')
  },
  {
    path: '/chat',
    name: 'AIChat',
    component: () => import('@/views/AIChat.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
