<template>
  <div>
    <el-card shadow="never">
      <div class="toolbar">
        <span class="tip">角色权限可自行配置：勾选权限即授予对应角色。</span>
        <div class="spacer" />
        <el-button v-if="store.has('role:manage')" type="success" :icon="Plus" @click="openCreate">新增角色</el-button>
      </div>
    </el-card>

    <el-row :gutter="12" style="margin-top:12px">
      <el-col :span="7">
        <el-card shadow="never" style="max-height:70vh;overflow:auto">
          <div
            v-for="r in roles"
            :key="r.id"
            class="role-item"
            :class="{ active: current?.id === r.id }"
            @click="select(r)"
          >
            <div class="role-name">
              {{ r.name }}
              <el-tag v-if="r.is_system" size="small" type="info" effect="plain">内置</el-tag>
            </div>
            <div class="role-desc">{{ r.description || '' }}</div>
          </div>
          <el-empty v-if="!roles.length" :image-size="60" />
        </el-card>
      </el-col>

      <el-col :span="17">
        <el-card shadow="never" v-if="current">
          <template #header>
            <div class="perm-header">
              <span>「{{ current.name }}」的权限</span>
              <div class="spacer" />
              <el-button size="small" type="primary" :loading="saving" @click="savePerms">保存权限</el-button>
              <el-button v-if="!current.is_system && store.has('role:manage')" size="small" type="danger" plain @click="remove(current)">删除角色</el-button>
            </div>
          </template>

          <div v-for="group in permGroups" :key="group.module" class="perm-group">
            <div class="group-title">{{ group.label }}</div>
            <el-checkbox-group v-model="selectedPerms">
              <el-checkbox v-for="p in group.perms" :key="p.id" :value="p.id" :disabled="!store.has('role:manage')">
                {{ p.name }}
                <span class="perm-code">{{ p.code }}</span>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="visible" title="新增角色" width="420px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="角色名称" required>
          <el-input v-model="form.name" placeholder="如：片区主管" />
        </el-form-item>
        <el-form-item label="角色编码" required>
          <el-input v-model="form.code" placeholder="如 region_leader" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" />
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { listRoles, listPermissions, createRole, updateRole, deleteRole } from '../api'
import { useAuthStore } from '../stores/auth'

const store = useAuthStore()
const roles = ref([])
const permissions = ref([])
const current = ref(null)
const selectedPerms = ref([])
const saving = ref(false)

const visible = ref(false)
const form = reactive({ name: '', code: '', description: '' })

const MODULE_LABEL = { user: '用户管理', org: '组织管理', role: '角色与权限', ticket: '工单', stats: '统计' }

const permGroups = computed(() => {
  const map = {}
  for (const p of permissions.value) {
    const label = MODULE_LABEL[p.module] || p.module
    ;(map[label] ||= { label, perms: [] }).perms.push(p)
  }
  return Object.values(map)
})

onMounted(async () => {
  roles.value = await listRoles()
  permissions.value = await listPermissions()
  if (roles.value.length) select(roles.value[0])
})

function select(r) {
  current.value = r
  selectedPerms.value = r.permissions.map((p) => p.id)
}

function openCreate() {
  Object.assign(form, { name: '', code: '', description: '' })
  visible.value = true
}

async function save() {
  if (!form.name || !form.code) return ElMessage.warning('请填写名称和编码')
  saving.value = true
  try {
    const r = await createRole(form)
    roles.value = await listRoles()
    select(r)
    visible.value = false
    ElMessage.success('角色已创建，请为其勾选权限')
  } finally {
    saving.value = false
  }
}

async function savePerms() {
  saving.value = true
  try {
    await updateRole(current.value.id, { permission_ids: selectedPerms.value })
    roles.value = await listRoles()
    select(roles.value.find((r) => r.id === current.value.id))
    ElMessage.success('权限已保存')
  } finally {
    saving.value = false
  }
}

async function remove(r) {
  await ElMessageBox.confirm(`确定删除角色「${r.name}」吗？`, '提示', { type: 'warning' })
  await deleteRole(r.id)
  roles.value = await listRoles()
  if (roles.value.length) select(roles.value[0])
  else current.value = null
  ElMessage.success('已删除')
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
}
.tip {
  color: #909399;
  font-size: 13px;
}
.spacer {
  flex: 1;
}
.role-item {
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 6px;
  border: 1px solid #ebeef5;
}
.role-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}
.role-name {
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}
.role-desc {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}
.perm-header {
  display: flex;
  align-items: center;
}
.perm-group {
  margin-bottom: 18px;
}
.group-title {
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f2f3f5;
}
.perm-code {
  color: #c0c4cc;
  font-size: 12px;
  margin-left: 4px;
}
</style>
