<template>
  <div class="profile-page">
    <el-card shadow="never" style="max-width:520px;margin:0 auto">
      <template #header>个人中心</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="账号">{{ store.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ store.user?.real_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所属组织">{{ store.user?.org?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ store.user?.role?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="权限">
          <el-tag v-for="p in (store.user?.role?.permissions || [])" :key="p.id" size="small" effect="plain" style="margin:2px">
            {{ p.name }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top:20px">修改密码</h4>
      <el-form :model="form" label-width="90px">
        <el-form-item label="原密码" required>
          <el-input v-model="form.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" required>
          <el-input v-model="form.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" required>
          <el-input v-model="form.confirm" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="save">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword } from '../api'
import { useAuthStore } from '../stores/auth'

const store = useAuthStore()
const saving = ref(false)
const form = reactive({ old_password: '', new_password: '', confirm: '' })

async function save() {
  if (!form.old_password || !form.new_password) return ElMessage.warning('请填写完整')
  if (form.new_password.length < 6) return ElMessage.warning('新密码至少 6 位')
  if (form.new_password !== form.confirm) return ElMessage.warning('两次输入的新密码不一致')
  saving.value = true
  try {
    await changePassword({ old_password: form.old_password, new_password: form.new_password })
    ElMessage.success('密码已修改，请重新登录')
    store.logout()
  } finally {
    saving.value = false
  }
}
</script>
