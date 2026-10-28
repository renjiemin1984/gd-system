<template>
  <div>
    <el-card shadow="never">
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索账号/姓名" clearable style="width:220px" @keyup.enter="load" />
        <el-button type="primary" :icon="Search" @click="load">查询</el-button>
        <div class="spacer" />
        <el-button v-if="store.has('user:manage')" type="success" :icon="Plus" @click="openCreate">新增用户</el-button>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" v-loading="loading">
        <el-table-column prop="username" label="账号" width="130" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column label="组织" width="140">
          <template #default="{ row }">{{ row.org?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.role?.name || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="store.has('user:manage')" size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="store.has('user:manage')" size="small" text type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !list.length" description="暂无用户" />
    </el-card>

    <el-dialog v-model="visible" :title="editing ? '编辑用户' : '新增用户'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="账号" required>
          <el-input v-model="form.username" :disabled="editing" placeholder="登录账号" />
        </el-form-item>
        <el-form-item v-if="!editing" label="密码" required>
          <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="所属组织">
          <el-select v-model="form.org_id" clearable filterable placeholder="选择组织" style="width:100%">
            <el-option v-for="o in flatOrgs" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_id" clearable filterable placeholder="选择角色" style="width:100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
        <el-form-item v-if="editing" label="重置密码">
          <el-input v-model="form.password" type="password" show-password placeholder="留空则不修改密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { listUsers, createUser, updateUser, deleteUser, listOrgs, listRoles } from '../api'
import { useAuthStore } from '../stores/auth'

const store = useAuthStore()
const list = ref([])
const roles = ref([])
const flatOrgs = ref([])
const loading = ref(false)
const keyword = ref('')
const visible = ref(false)
const editing = ref(false)
const saving = ref(false)
const form = reactive({ username: '', password: '', real_name: '', phone: '', org_id: null, role_id: null, is_active: true })

onMounted(async () => {
  flatOrgs.value = await listOrgs(true)
  roles.value = await listRoles()
  load()
})

async function load() {
  loading.value = true
  try {
    list.value = await listUsers({ keyword: keyword.value || undefined })
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = false
  Object.assign(form, { username: '', password: '', real_name: '', phone: '', org_id: null, role_id: null, is_active: true })
  visible.value = true
}

function openEdit(row) {
  editing.value = true
  Object.assign(form, { username: row.username, password: '', real_name: row.real_name, phone: row.phone, org_id: row.org_id, role_id: row.role_id, is_active: row.is_active })
  visible.value = true
}

async function save() {
  if (!form.username) return ElMessage.warning('请输入账号')
  if (!editing.value && form.password.length < 6) return ElMessage.warning('密码至少 6 位')
  saving.value = true
  try {
    const payload = { ...form }
    if (editing.value && !payload.password) delete payload.password
    if (editing.value) await updateUser(list.value.find((u) => u.username === form.username).id, payload)
    else await createUser(payload)
    ElMessage.success('保存成功')
    visible.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除用户「${row.real_name || row.username}」吗？`, '提示', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('已删除')
  load()
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
}
.spacer {
  flex: 1;
}
</style>
