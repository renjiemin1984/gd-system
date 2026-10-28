import { useAuthStore } from '../stores/auth'

// 简单权限工具：供路由守卫使用（store 需在调用时获取）
export function can(store, code) {
  if (!store) return false
  return store.has(code)
}

export const STATUS_TEXT = {
  pending: '待处理',
  processing: '处理中',
  resolved: '已解决',
  closed: '已关闭',
}

export const STATUS_TAG = {
  pending: 'warning',
  processing: 'primary',
  resolved: 'success',
  closed: 'info',
}

export const PRIORITY_TEXT = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '紧急',
}

export const PRIORITY_TAG = {
  low: 'info',
  medium: '',
  high: 'warning',
  urgent: 'danger',
}
