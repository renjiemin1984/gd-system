<template>
  <div>
    <el-card shadow="never">
      <el-form inline>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部状态" style="width:120px">
            <el-option v-for="(t, k) in STATUS_TEXT" :key="k" :label="t" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.type_id" clearable placeholder="全部类型" style="width:130px">
            <el-option v-for="t in types" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filters.priority" clearable placeholder="全部" style="width:110px">
            <el-option v-for="(t, k) in PRIORITY_TEXT" :key="k" :label="t" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="工地">
          <el-select v-model="filters.org_id" clearable filterable placeholder="全部工地" style="width:160px">
            <el-option v-for="o in siteOrgs" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="编号/标题/描述" clearable style="width:180px" @keyup.enter="load" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="filters.mine">只看我提交的</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="load">查询</el-button>
          <el-button :icon="Refresh" @click="reset">重置</el-button>
          <el-button v-if="store.has('ticket:create')" type="success" :icon="CirclePlus" @click="$router.push('/tickets/create')">提交工单</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" v-loading="loading">
        <el-table-column prop="code" label="编号" width="150" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.type?.name || '待分类' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="工地" width="120">
          <template #default="{ row }">{{ row.site_org?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="提交人" width="100">
          <template #default="{ row }">{{ row.creator?.real_name || row.creator?.username || '-' }}</template>
        </el-table-column>
        <el-table-column label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="PRIORITY_TAG[row.priority]">{{ PRIORITY_TEXT[row.priority] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="STATUS_TAG[row.status]">{{ STATUS_TEXT[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="160">
          <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="$router.push(`/tickets/${row.id}`)">详情</el-button>
            <el-button v-if="store.has('ticket:handle') && row.status==='pending'" size="small" text type="warning" @click="quickHandle(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !list.length" description="暂无工单" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Search, Refresh, CirclePlus } from '@element-plus/icons-vue'
import { listTickets, listTicketTypes, listOrgs, handleTicket } from '../api'
import { useAuthStore } from '../stores/auth'
import { STATUS_TEXT, STATUS_TAG, PRIORITY_TEXT, PRIORITY_TAG } from '../utils/permission'

const store = useAuthStore()
const loading = ref(false)
const list = ref([])
const types = ref([])
const siteOrgs = ref([])
const filters = reactive({ status: '', type_id: null, priority: '', org_id: null, keyword: '', mine: false })

onMounted(async () => {
  types.value = await listTicketTypes()
  const orgs = await listOrgs(true)
  siteOrgs.value = orgs.filter((o) => o.type === 'site')
  load()
})

async function load() {
  loading.value = true
  try {
    const params = { ...filters }
    for (const k of Object.keys(params)) if (!params[k] && params[k] !== false) delete params[k]
    list.value = await listTickets(params)
  } finally {
    loading.value = false
  }
}

function reset() {
  Object.assign(filters, { status: '', type_id: null, priority: '', org_id: null, keyword: '', mine: false })
  load()
}

async function quickHandle(row) {
  try {
    const { value } = await ElMessageBox.prompt('填写处理说明', `处理工单 ${row.code}`, {
      confirmButtonText: '标记已解决',
      cancelButtonText: '仅开始处理',
      inputPlaceholder: '请描述处理方式/结果',
      distinguishCancelAndClose: true,
    })
    await handleTicket(row.id, { status: 'resolved', resolution: value || undefined })
  } catch (e) {
    if (e === 'cancel') {
      await handleTicket(row.id, { status: 'processing' })
    } else if (e !== 'close') {
      return
    }
  }
  load()
}

function formatTime(t) {
  return t ? t.replace('T', ' ').slice(0, 16) : '-'
}
</script>
