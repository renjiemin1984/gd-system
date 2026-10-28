<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.key">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-num" :style="{ color: card.color }">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>按类型分布</template>
          <div v-if="typeTotal">
            <div class="bar-row" v-for="t in stats.by_type" :key="t.name">
              <span class="bar-label">{{ t.name }}</span>
              <el-progress :percentage="Math.round((t.value / typeTotal) * 100)" :stroke-width="16" />
              <span class="bar-val">{{ t.value }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>按工地分布</template>
          <div v-if="orgTotal">
            <div class="bar-row" v-for="o in stats.by_org" :key="o.name">
              <span class="bar-label">{{ o.name }}</span>
              <el-progress :percentage="Math.round((o.value / orgTotal) * 100)" :stroke-width="16" :color="'#409eff'" />
              <span class="bar-val">{{ o.value }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top:16px">
      <template #header>最新工单</template>
      <el-table :data="stats.recent" size="small" @row-click="goDetail" style="cursor:pointer">
        <el-table-column prop="code" label="编号" width="150" />
        <el-table-column prop="title" label="标题" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ row.type?.name || '待分类' }}</template>
        </el-table-column>
        <el-table-column label="工地" width="120">
          <template #default="{ row }">{{ row.site_org?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="STATUS_TAG[row.status]">{{ STATUS_TEXT[row.status] }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getStats } from '../api'
import { STATUS_TEXT, STATUS_TAG } from '../utils/permission'

const router = useRouter()
const stats = ref({ total: 0, by_status: {}, by_type: [], by_org: [], recent: [] })

const cards = computed(() => [
  { key: 'total', label: '工单总数', value: stats.value.total, color: '#409eff' },
  { key: 'pending', label: '待处理', value: stats.value.by_status?.pending || 0, color: '#e6a23c' },
  { key: 'processing', label: '处理中', value: stats.value.by_status?.processing || 0, color: '#409eff' },
  { key: 'resolved', label: '已解决', value: stats.value.by_status?.resolved || 0, color: '#67c23a' },
])

const typeTotal = computed(() => stats.value.by_type.reduce((a, b) => a + b.value, 0))
const orgTotal = computed(() => stats.value.by_org.reduce((a, b) => a + b.value, 0))

onMounted(async () => {
  stats.value = await getStats()
})

function goDetail(row) {
  router.push(`/tickets/${row.id}`)
}
</script>

<style scoped>
.stat-card {
  text-align: center;
}
.stat-num {
  font-size: 34px;
  font-weight: 700;
}
.stat-label {
  margin-top: 4px;
  color: #909399;
  font-size: 14px;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.bar-label {
  width: 70px;
  text-align: right;
  color: #606266;
  flex-shrink: 0;
}
.bar-row .el-progress {
  flex: 1;
}
.bar-val {
  width: 40px;
  color: #606266;
}
</style>
