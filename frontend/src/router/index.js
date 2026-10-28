import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '统计看板', need: 'stats:read' } },
      { path: 'tickets', name: 'tickets', component: () => import('../views/TicketList.vue'), meta: { title: '工单列表', need: 'ticket:create' } },
      { path: 'tickets/create', name: 'ticketCreate', component: () => import('../views/TicketCreate.vue'), meta: { title: '提交工单', need: 'ticket:create' } },
      { path: 'tickets/:id', name: 'ticketDetail', component: () => import('../views/TicketDetail.vue'), meta: { title: '工单详情', need: 'ticket:create' } },
      { path: 'types', name: 'types', component: () => import('../views/TypeManage.vue'), meta: { title: '工单类型', need: 'ticket:manage' } },
      { path: 'users', name: 'users', component: () => import('../views/UserManage.vue'), meta: { title: '用户管理', need: 'user:read' } },
      { path: 'orgs', name: 'orgs', component: () => import('../views/OrgManage.vue'), meta: { title: '组织管理', need: 'org:read' } },
      { path: 'roles', name: 'roles', component: () => import('../views/RoleManage.vue'), meta: { title: '角色权限', need: 'role:read' } },
      { path: 'profile', name: 'profile', component: () => import('../views/Profile.vue'), meta: { title: '个人中心' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const store = useAuthStore()
  if (to.path === '/login') {
    if (store.isLoggedIn) return '/dashboard'
    return true
  }
  if (!store.isLoggedIn) return '/login'
  if (to.meta.need && !store.has(to.meta.need)) return '/dashboard'
  return true
})

export default router
