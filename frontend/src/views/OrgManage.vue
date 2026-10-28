<template>
  <div>
    <el-card shadow="never">
      <div class="toolbar">
        <span class="tip">组织架构：公司 → 项目部 → 工地。工地用户提交的工单归属对应工地。</span>
        <div class="spacer" />
        <el-button v-if="store.has('org:manage')" type="success" :icon="Plus" @click="openCreate(null)">新增组织</el-button>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="tree" row-key="id" :tree-props="{ children: 'children' }" v-loading="loading" default-expand-all>
        <el-table-column prop="name" label="组织名称" min-width="200" />
        <el-table-column prop="code" label="编码" width="140" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="{ company: 'danger', project: 'warning', site: 'success' }[row.type]">
              {{ { company: '公司', project: '项目部', site: '工地' }[row.type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="store.has('org:manage')">
              <el-button size="small" text type="primary" @click="openCreate(row)">添加下级</el-button>
              <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" text type="danger" @click="remove(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="visible" :title="editing ? '编辑组织' : (form.parent_id ? '新增下级组织' : '新增组织')" width="460px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="编码" required>
          <el-input v-model="form.code" :disabled="editing" placeholder="如 SITE-A01" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width:100%">
            <el-option label="公司" value="company" />
            <el-option label="项目部" value="project" />
            <el-option label="工地" value="site" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!editing && !form.parent_id" label="上级组织">
          <el-select v-model="form.parent_id" clearable filterable placeholder="不选则为顶级" style="width:100%">
            <el-option v-for="o in flatOrgs" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { listOrgs, createOrg, updateOrg, deleteOrg } from '../api'
import { useAuthStore } from '../stores/auth'

const store = useAuthStore()
const tree = ref([])
const flatOrgs = ref([])
const loading = ref(false)
const visible = ref(false)
const editing = ref(false)
const saving = ref(false)
const form = reactive({ id: null, name: '', code: '', type: 'site', parent_id: null, description: '' })

async function load() {
  loading.value = true
  try {
    tree.value = await listOrgs(false)
    flatOrgs.value = await listOrgs(true)
  } finally {
    loading.value = false
  }
}
onMounted(load)

function openCreate(parent) {
  editing.value = false
  Object.assign(form, { id: null, name: '', code: '', type: parent ? 'site' : 'company', parent_id: parent ? parent.id : null, description: '' })
  visible.value = true
}

function openEdit(row) {
  editing.value = true
  Object.assign(form, { id: row.id, name: row.name, code: row.code, type: row.type, parent_id: row.parent_id, description: row.description })
  visible.value = true
}

async function save() {
  if (!form.name || !form.code) return ElMessage.warning('请填写名称和编码')
  saving.value = true
  try {
    const payload = { name: form.name, code: form.code, type: form.type, description: form.description }
    if (editing.value) await updateOrg(form.id, payload)
    else await createOrg({ ...payload, parent_id: form.parent_id })
    ElMessage.success('保存成功')
    visible.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除组织「${row.name}」吗？`, '提示', { type: 'warning' })
  await deleteOrg(row.id)
  ElMessage.success('已删除')
  load()
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
</style>
