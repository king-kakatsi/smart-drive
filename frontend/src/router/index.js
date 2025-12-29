import { createRouter, createWebHistory } from 'vue-router'
import authenticationService from '@/services/api/authenticationService'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/files/:folderPath*',
    name: 'FileExplorer',
    component: () => import('../views/FileExplorer.vue'),
    props: route => ({
      initialFolderPath: '/' + (route.params.folderPath || []).join('/')
    }),
    meta: { requiresAuth: true }
  },
  {
    path: '/recent',
    name: 'Recent',
    component: () => import('../views/Recent.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/starred',
    name: 'Starred',
    component: () => import('../views/Starred.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/trash',
    name: 'Trash',
    component: () => import('../views/Trash.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'AIChat',
    component: () => import('../views/AIChat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('../views/AuthCallback.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const isAuthenticated = authenticationService.isAuthenticated()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !isAuthenticated) {
    // Redirect to login if route requires auth and user is not authenticated
    next({ name: 'Login' })
  } else if (to.name === 'Login' && isAuthenticated) {
    // Redirect to dashboard if user is already authenticated and tries to access login
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
