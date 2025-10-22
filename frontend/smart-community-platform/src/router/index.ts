import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    // 捕获所有未匹配的路由，重定向到登录页
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// 路由守卫，检查是否需要登录
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const hasToken = localStorage.getItem('token')
  
  if (requiresAuth && !hasToken) {
    // 需要登录但没有token，重定向到登录页
    next('/')
  } else {
    // 不需要登录或者已经有token，可以继续访问
    next()
  }
})

export default router
