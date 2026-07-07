/** 路由配置 */
import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { title: '工作台', icon: 'DataAnalysis' },
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/materials/Index.vue'),
        meta: { title: '个人素材库', icon: 'Folder' },
      },
      {
        path: 'jd',
        name: 'JDManage',
        component: () => import('@/views/jd/Index.vue'),
        meta: { title: 'JD智能解析', icon: 'Document' },
      },
      {
        path: 'jd/:id',
        name: 'JDDetail',
        component: () => import('@/views/jd/Detail.vue'),
        meta: { title: 'JD详情', hidden: true },
      },
      {
        path: 'resumes',
        name: 'Resumes',
        component: () => import('@/views/resumes/Index.vue'),
        meta: { title: '简历管理', icon: 'Notebook' },
      },
      {
        path: 'resumes/:id',
        name: 'ResumeDetail',
        component: () => import('@/views/resumes/Detail.vue'),
        meta: { title: '简历详情', hidden: true },
      },
      {
        path: 'delivery',
        name: 'Delivery',
        component: () => import('@/views/delivery/Index.vue'),
        meta: { title: '投递管理', icon: 'Send' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Index.vue'),
        meta: { title: '系统设置', icon: 'Setting' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫 — 未登录跳转登录页
router.beforeEach((to, from, next) => {
  const token = getToken()
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
