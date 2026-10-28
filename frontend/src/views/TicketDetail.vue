<template>
  <div v-if="ticket" class="detail-page">
    <el-page-header :content="`${ticket.code} - ${ticket.title}`" @back="$router.back()" style="margin-bottom:12px" />

    <el-row :gutter="16">
      <el-col :span="16">
        <el-card shadow="never">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="状态">
              <el-tag :type="STATUS_TAG[ticket.status]">{{ STATUS_TEXT[ticket.status] }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="优先级">
              <el-tag :type="PRIORITY_TAG[ticket.priority]">{{ PRIORITY_TEXT[ticket.priority] }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="类型">
              <el-tag effect="plain">{{ ticket.type?.name || '待分类' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="工地">{{ ticket.site_org?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="提交人">{{ ticket.creator?.real_name || ticket.creator?.username }}</el-descriptions-item>
            <el-descriptions-item label="提交时间">{{ fmt(ticket.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="处理人">{{ ticket.assignee?.real_name || ticket.assignee?.username || '未指派' }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ fmt(ticket.updated_at) }}</el-descriptions-item>
          </el-descriptions>

          <h4>问题描述</h4>
          <div class="desc">{{ ticket.description || '（无详细描述）' }}</div>

          <h4 v-if="ticket.resolution">处理结果</h4>
          <div v-if="ticket.resolution" class="desc resolution">{{ ticket.resolution }}</div>

          <div class="actions" v-if="store.has('ticket:handle')">
            <el-button v-if="ticket.status==='pending'" type="primary" @click="openHandle('processing')">开始处理</el-button>
            <el-button v-if="ticket.status==='pending' || ticket.status==='processing'" type="success" @click="openHandle('resolved')">标记已解决</el-button>
            <el-button v-if="ticket.status==='resolved'" type="warning" @click="openHandle('closed')">关闭工单</el-button>
            <el-button v-if="store.has('ticket:manage')" type="info" @click="openClassify">重新归类</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never">
          <template #header>流转记录</template>
          <el-timeline>
            <el-timeline-item v-for="log in ticket.logs" :key="log.id" :timestamp="fmt(log.created_at)" placement="top">
              <b>{{ actionText[log.action] || log.action }}</b>
              <div class="log-op">{{ log.operator?.real_name || log.operator?.username || '系统' }}</div>
              <div v-if="log.remark" class="log-remark">{{ log.remark }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 处理弹窗 -->
    <el-dialog v-model="handleVisible" :title="handleTitle" width="520px">
      <el-form label-width="80px">
        <el-form-item label="处理说明">
          <el-input v-model="handleForm.resolution" type="textarea" :rows="4" placeholder="填写处理方式、结果或下一步安排" />
        </el-form-item>
        <el-form-item label="指派处理人" v-if="store.has('ticket:handle')">
          <el-select v-model="handleForm.assignee_id" clearable filterable placeholder="选择处理人（可选）" style="width:100%">
            <el-option v-for="u in staffs" :key="u.id" :label="u.real_name || u.username" :value="u.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleVisible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doHandle">保存</el-button>
      </template>
    </el-dialog>

    <!-- 重新归类弹窗 -->
    <el-dialog v-model="classifyVisible" title="重新归类" width="420px">
      <el-select v-model="classifyType" style="width:100%" placeholder="选择工单类型">
        <el-option v-for="t in types" :key="t.id" :label="t.name" :value="t.id" />
      </el-select>
      <template #footer>
        <el-button @click="classifyVisible=false">取消</el-button>
        <el-button type="primary" @click="doClassify">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTicket, handleTicket, reclassifyTicket, listTicketTypes, listUsers } from '../api'
import { useAuthStore } from '../stores/auth'
import { STATUS_TEXT, STATUS_TAG, PRIORITY_TEXT, PRIORITY_TAG } from '../utils/permission'

const route = useRoute()
const store = useAuthStore()
const ticket = ref(null)
const types = ref([])
const staffs = ref([])

const actionText = { create: '提交工单', assign: '指派处理人', status: '状态变更', classify: '重新归类', comment: '评论' }

const handleVisible = ref(false)
const handleTitle = ref('')
const handleForm = ref({ status: '', resolution: '', assignee_id: null })
const saving = ref(false)

const classifyVisible = ref(false)
const classifyType = ref(null)

onMounted(load)
async function load() {
  ticket.value = await getTicket(route.params.id)
  types.value = await listTicketTypes()
  if (store.has('ticket:handle')) staffs.value = await listUsers({})
}

function fmt(t) { return t ? t.replace('T', ' ').slice(0, 16) : '-' }

function openHandle(status) {
  handleForm.value = { status, resolution: status === 'closed' ? ticket.value.resolution || '' : '', assignee_id: null }
  handleTitle.value = { processing: '开始处理', resolved: '标记已解决', closed: '关闭工单' }[status]
  handleVisible.value = true
}

async function doHandle() {
  saving.value = true
  try {
    const payload = { status: handleForm.value.status }
    if (handleForm.value.resolution) payload.resolution = handleForm.value.resolution
    if (handleForm.value.assignee_id) payload.assignee_id = handleForm.value.assignee_id
    ticket.value = await handleTicket(ticket.value.id, payload)
    handleVisible.value = false
    ElMessage.success('已保存')
  } finally {
    saving.value = false
  }
}

function openClassify() {
  classifyType.value = ticket.value.type_id
  classifyVisible.value = true
}

async function doClassify() {
  if (!classifyType.value) return ElMessage.warning('请选择类型')
  ticket.value = await reclassifyTicket(ticket.value.id, { type_id: classifyType.value })
  classifyVisible.value = false
  ElMessage.success('归类已更新')
}
</script>

<style scoped>
.desc {
  color: #303133;
  line-height: 1.7;
  white-space: pre-wrap;
  background: #f7f8fa;
  padding: 12px;
  border-radius: 6px;
}
.resolution {
  background: #f0f9eb;
  color: #529b2e;
}
.actions {
  margin-top: 16px;
}
.log-op {
  color: #909399;
  font-size: 12px;
}
.log-remark {
  margin-top: 4px;
  color: #606266;
}
</style>
