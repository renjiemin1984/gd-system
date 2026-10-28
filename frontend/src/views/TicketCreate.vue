<template>
  <div class="create-page">
    <el-card shadow="never" style="max-width:860px;margin:0 auto">
      <template #header>提交工单</template>
      <el-form :model="form" label-width="90px">
        <el-form-item label="问题标题" required>
          <el-input v-model="form.title" maxlength="128" show-word-limit placeholder="一句话概括工地上的问题，如：三号塔吊钢丝绳磨损严重" @input="preview" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model="form.description" type="textarea" :rows="5" placeholder="详细描述问题发生的位置、现象、影响等，系统将据此自动归类" @input="preview" />
        </el-form-item>
        <el-form-item label="所属工地">
          <el-select v-model="form.site_org_id" placeholder="选择工地（默认你的所属组织）" style="width:100%" filterable>
            <el-option v-for="o in siteOrgs" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio-button v-for="(t, k) in PRIORITY_TEXT" :key="k" :label="k">{{ t }}</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="自动归类">
          <el-tag v-if="previewType" size="large" effect="dark" type="primary">{{ previewType.name }}</el-tag>
          <el-tag v-else size="large" effect="plain" type="info">待分类（暂未匹配到类型）</el-tag>
          <span class="hint">根据标题/描述中的关键词自动匹配，提交后由系统最终确定</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="submitting" @click="submit">提交工单</el-button>
          <el-button size="large" @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { listTicketTypes, listOrgs, createTicket } from '../api'
import { useAuthStore } from '../stores/auth'
import { PRIORITY_TEXT } from '../utils/permission'

const router = useRouter()
const store = useAuthStore()
const types = ref([])
const siteOrgs = ref([])
const previewType = ref(null)
const submitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  site_org_id: store.user?.org_id || null,
  priority: 'medium',
})

onMounted(async () => {
  types.value = await listTicketTypes()
  const orgs = await listOrgs(true)
  siteOrgs.value = orgs.filter((o) => o.type === 'site')
})

// 客户端预览：与后端同一套关键词规则（标题权重 2，描述权重 1）
function preview() {
  const text = `${form.title} ${form.description}`
  let best = null
  let bestScore = 0
  for (const t of types.value) {
    if (t.code === 'uncategorized' || !t.keywords) continue
    const kws = t.keywords.split(',').map((s) => s.trim()).filter(Boolean)
    let score = 0
    for (const kw of kws) score += (form.title.match(new RegExp(kw, 'g')) || []).length * 2 + (text.match(new RegExp(kw, 'g')) || []).length
    if (score > bestScore) {
      bestScore = score
      best = t
    }
  }
  previewType.value = bestScore > 0 ? best : null
}

async function submit() {
  if (!form.title.trim()) return ElMessage.warning('请填写问题标题')
  submitting.value = true
  try {
    const t = await createTicket(form)
    ElMessage.success(`工单已提交，编号：${t.code}，系统归类为「${t.type?.name || '待分类'}」`)
    router.push(`/tickets/${t.id}`)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.hint {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}
</style>
