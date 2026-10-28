<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">🏗️ 工地工单系统</div>
      <el-menu :default-active="$route.path" router background-color="#1f3a5f" text-color="#c8d4e0" active-text-color="#fff">
        <el-menu-item index="/dashboard" v-if="store.has('stats:read')">
          <el-icon><DataAnalysis /></el-icon><span>统计看板</span>
        </el-menu-item>
        <el-menu-item index="/tickets" v-if="store.has('ticket:create')">
          <el-icon><Tickets /></el-icon><span>工单列表</span>
        </el-menu-item>
        <el-menu-item index="/tickets/create" v-if="store.has('ticket:create')">
          <el-icon><CirclePlus /></el-icon><span>提交工单</span>
        </el-menu-item>
        <el-menu-item index="/types" v-if="store.has('ticket:manage')">
          <el-icon><SetUp /></el-icon><span>工单类型</span>
        </el-menu-item>
        <el-sub-menu index="sys" v-if="store.has('user:read') || store.has('org:read') || store.has('role:read')">
          <template #title><el-icon><Setting /></el-icon><span>系统管理</span></template>
          <el-menu-item index="/users" v-if="store.has('user:read')">用户管理</el-menu-item>
          <el-menu-item index="/orgs" v-if="store.has('org:read')">组织管理</el-menu-item>
          <el-menu-item index="/roles" v-if="store.has('role:read')">角色权限</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="page-title">{{ $route.meta.title || '' }}</div>
        <el-dropdown @command="onCommand">
          <span class="user">
            <el-avatar :size="30" style="background:#2c5f8a">{{ avatarChar }}</el-avatar>
            <span class="name">{{ store.user?.real_name || store.user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const store = useAuthStore()

const avatarChar = computed(() => (store.user?.real_name || store.user?.username || 'U').slice(0, 1))

async function onCommand(cmd) {
  if (cmd === 'profile') return router.push('/profile')
  if (cmd === 'logout') {
    await ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
    store.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout {
  height: 100%;
}
.aside {
  background: #1f3a5f;
  display: flex;
  flex-direction: column;
}
.logo {
  height: 60px;
  line-height: 60px;
  color: #fff;
  font-weight: 600;
  text-align: center;
  font-size: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.aside :deep(.el-menu) {
  border-right: none;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.user {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.name {
  color: #303133;
}
.main {
  background: #f5f7fa;
  padding: 16px;
  overflow: auto;
}
</style>
