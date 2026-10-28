<template>
  <div>
    <el-card shadow="never">
      <div class="toolbar">
        <span class="tip">配置工单类型的分类关键词，提交工单时系统据此自动归类（标题权重 2，描述权重 1，命中最多者胜出）。</span>
        <div class="spacer" />
        <el-button v-if="store.has('ticket:manage')" type="success" :icon="Plus" @click="openCreate">新增类型</el-button>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" v-loading="loading">
        <el-table-column prop="name" label="类型名称" width="160" />
        <el-table-column prop="code" label="编码" width="160" />
        <el-table-column prop="keywords" label="分类关键词（逗号分隔）" min-width="260" />
        <el-table-column prop="sort" label="排序" width="70" />
        <el-table-column prop="description" label="说明" min-width="140" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <template v-if="store.has('ticket:manage')">
              <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button v-if="row.code !== 'uncategorized'" size="small" text type="danger" @click="remove(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="visible" :title="editing ? '编辑类型' : '新增类型'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="类型名称" required>
          <el-input v-model="form.name" placeholder="如：安全事故" />
        </el-form-item>
        <el-form-item label="编码" required>
          <el-input v-model="form.code" :disabled="editing" placeholder="如 safety" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="form.keywords" type="textarea" :rows="3" placeholder="用英文逗号分隔，如：坠落,倒塌,坍塌,围挡,防护,隐患,事故" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :max="999" />
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
import { listTicketTypes, createTicketType, updateTicketType, deleteTicketType } from '../api'
import { useAuthStore } from '../stores/auth'

const store = useAuthStore()
const list = ref([])
const loading = ref(false)
const visible = ref(false)
const editing = ref(false)
const saving = ref(false)
const form = reactive({ id: null, name: '', code: '', keywords: '', sort: 0, description: '' })

async function load() {
  loading.value = true
  try {
    list.value = await listTicketTypes()
  } finally {
    loading.value = false
  }
}
onMounted(load)

function openCreate() {
  editing.value = false
  Object.assign(form, { id: null, name: '', code: '', keywords: '', sort: 0, description: '' })
  visible.value = true
}

function openEdit(row) {
  editing.value = true
  Object.assign(form, { id: row.id, name: row.name, code: row.code, keywords: row.keywords || '', sort: row.sort, description: row.description })
  visible.value = true
}

async function save() {
  if (!form.name || !form.code) return ElMessage.warning('请填写名称和编码')
  saving.value = true
  try {
    if (editing.value) await updateTicketType(form.id, { name: form.name, keywords: form.keywords, sort: form.sort, description: form.description })
    else await createTicketType(form)
    ElMessage.success('保存成功')
    visible.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除类型「${row.name}」吗？`, '提示', { type: 'warning' })
  await deleteTicketType(row.id)
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
