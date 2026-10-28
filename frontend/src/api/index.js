import request from './request'

// 认证
export const login = (data) => request.post('/auth/login', data)
export const getMe = () => request.get('/auth/me')
export const changePassword = (data) => request.put('/auth/password', data)

// 用户
export const listUsers = (params) => request.get('/users', { params })
export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.put(`/users/${id}`, data)
export const deleteUser = (id) => request.delete(`/users/${id}`)

// 组织
export const listOrgs = (flat = false) => request.get('/orgs', { params: { flat } })
export const createOrg = (data) => request.post('/orgs', data)
export const updateOrg = (id, data) => request.put(`/orgs/${id}`, data)
export const deleteOrg = (id) => request.delete(`/orgs/${id}`)

// 角色 / 权限
export const listRoles = () => request.get('/roles')
export const listPermissions = () => request.get('/roles/permissions')
export const createRole = (data) => request.post('/roles', data)
export const updateRole = (id, data) => request.put(`/roles/${id}`, data)
export const deleteRole = (id) => request.delete(`/roles/${id}`)

// 工单
export const listTickets = (params) => request.get('/tickets', { params })
export const getTicket = (id) => request.get(`/tickets/${id}`)
export const createTicket = (data) => request.post('/tickets', data)
export const updateTicket = (id, data) => request.put(`/tickets/${id}`, data)
export const handleTicket = (id, data) => request.put(`/tickets/${id}/handle`, data)
export const reclassifyTicket = (id, data) => request.put(`/tickets/${id}/classify`, data)

// 工单类型
export const listTicketTypes = () => request.get('/tickets/types')
export const createTicketType = (data) => request.post('/tickets/types', data)
export const updateTicketType = (id, data) => request.put(`/tickets/types/${id}`, data)
export const deleteTicketType = (id) => request.delete(`/tickets/types/${id}`)

// 统计
export const getStats = () => request.get('/stats')
