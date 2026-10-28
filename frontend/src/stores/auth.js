import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('gd_token') || '',
    user: JSON.parse(localStorage.getItem('gd_user') || 'null'),
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    permissions: (s) => {
      const perms = s.user?.role?.permissions || []
      return new Set(perms.map((p) => p.code))
    },
  },
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('gd_token', token)
      localStorage.setItem('gd_user', JSON.stringify(user))
    },
    setUser(user) {
      this.user = user
      localStorage.setItem('gd_user', JSON.stringify(user))
    },
    has(code) {
      return this.permissions.has(code)
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('gd_token')
      localStorage.removeItem('gd_user')
    },
  },
})
