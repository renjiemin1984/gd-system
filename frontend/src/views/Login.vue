<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <h2>🏗️ 工地工单管理系统</h2>
        <p>提交问题 · 统一处理 · 自动归类</p>
      </div>
      <el-form :model="form" @submit.prevent="onLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="账号" size="large" :prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password :prefix-icon="Lock" @keyup.enter="onLogin" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="onLogin">登 录</el-button>
      </el-form>
      <el-alert class="tip" type="info" :closable="false">
        默认账号：admin / admin123（系统管理员）
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '../api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const store = useAuthStore()
const loading = ref(false)
const form = reactive({ username: 'admin', password: 'admin123' })

async function onLogin() {
  if (!form.username || !form.password) return ElMessage.warning('请输入账号和密码')
  loading.value = true
  try {
    const res = await login(form)
    store.setAuth(res.access_token, res.user)
    ElMessage.success(`欢迎，${res.user.real_name || res.user.username}`)
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f3a5f 0%, #2c5f8a 100%);
}
.login-card {
  width: 380px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}
.brand {
  text-align: center;
  margin-bottom: 28px;
}
.brand h2 {
  margin: 0 0 6px;
  color: #1f3a5f;
}
.brand p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}
.tip {
  margin-top: 20px;
}
</style>
