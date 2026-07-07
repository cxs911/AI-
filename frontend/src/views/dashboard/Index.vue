<template>
  <div class="page-container">
    <!-- ===== 统计卡片 ===== -->
    <div class="stat-grid">
      <div class="stat-card" v-for="s in statCards" :key="s.key">
        <div class="stat-icon" :style="{ background: s.iconBg, color: s.iconColor }">
          <el-icon :size="20"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
          <div v-if="s.trend" class="stat-trend" :class="s.trendDir">
            {{ s.trend }}
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 欢迎引导（空状态） ===== -->
    <div v-if="isNewUser" class="welcome-card card">
      <div class="welcome-content">
        <div class="welcome-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <rect x="4" y="4" width="56" height="56" rx="16" fill="#EFF6FF"/>
            <path d="M32 20v24M20 32h24" stroke="#3B82F6" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <h3>欢迎使用 AI 求职助手 🎉</h3>
        <p>上传你的简历，让 AI 帮你匹配心仪的岗位，一键生成定制简历和招呼语。</p>
        <div class="welcome-steps">
          <div class="step" v-for="(step, i) in guideSteps" :key="i">
            <div class="step-num">{{ i + 1 }}</div>
            <div class="step-text">
              <strong>{{ step.title }}</strong>
              <span>{{ step.desc }}</span>
            </div>
          </div>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="$router.push('/materials')">
            <el-icon><Upload /></el-icon>上传简历
          </el-button>
          <el-button size="large" @click="$router.push('/jd')">
            <el-icon><DocumentAdd /></el-icon>添加 JD
          </el-button>
        </div>
      </div>
    </div>

    <!-- ===== 主内容（有数据时） ===== -->
    <template v-if="!isNewUser">
      <!-- 投递漏斗 -->
      <div class="card" v-if="hasDeliveryData">
        <div class="card-header">
          <h3>投递漏斗</h3>
        </div>
        <div class="funnel-grid">
          <div class="funnel-item" v-for="f in funnelData" :key="f.key">
            <div class="funnel-value">{{ f.value }}</div>
            <div class="funnel-label">{{ f.label }}</div>
            <div class="funnel-bar">
              <div class="funnel-fill" :style="{ width: f.pct + '%', background: f.color }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 双栏布局 -->
      <el-row :gutter="20">
        <!-- 左栏：最近投递 -->
        <el-col :xs="24" :lg="16">
          <div class="card">
            <div class="card-header">
              <h3>最近投递记录</h3>
              <span class="card-extra" v-if="recentDeliveries.length">
                共 {{ stats.totalDelivered }} 次投递
              </span>
            </div>
            <el-table
              :data="recentDeliveries"
              stripe
              v-loading="loading"
              style="width: 100%"
              empty-text=" "
            >
              <el-table-column prop="title" label="岗位" min-width="160">
                <template #default="{ row }">
                  <div class="job-cell">
                    <span class="job-title">{{ row.title }}</span>
                    <span class="job-company">{{ row.company }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="delivery_status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.delivery_status)" size="small" effect="plain" round>
                    {{ statusLabel(row.delivery_status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :prop="matchScoreField" label="匹配度" width="90" align="center">
                <template #default="{ row }">
                  <span class="match-score" :class="matchLevel(row.match_score)">
                    {{ row.match_score || '-' }}<template v-if="row.match_score">%</template>
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="delivered_at" label="时间" width="160" />
            </el-table>

            <div v-if="!recentDeliveries.length && !loading" class="empty-state" style="padding: 40px 0;">
              <el-icon class="empty-icon" :size="36"><Promotion /></el-icon>
              <h4>暂无投递记录</h4>
              <p>开始搜索岗位并投递，这里会展示你的投递动态</p>
              <div class="empty-actions">
                <el-button type="primary" @click="$router.push('/delivery')">
                  前往投递管理
                </el-button>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右栏：系统状态 + 快捷操作 -->
        <el-col :xs="24" :lg="8">
          <!-- 系统状态 -->
          <div class="card" style="margin-bottom: 20px;">
            <div class="card-header">
              <h3>系统状态</h3>
            </div>
            <div class="status-list">
              <div class="status-row" v-for="item in systemStatus" :key="item.label">
                <span class="status-row-label">{{ item.label }}</span>
                <span v-if="item.type === 'tag'" class="status-row-value">
                  <el-tag :type="item.status ? 'success' : 'danger'" size="small" effect="plain" round>
                    {{ item.status ? '正常' : '离线' }}
                  </el-tag>
                </span>
                <span v-else class="status-row-value">
                  {{ item.value }}
                </span>
              </div>
            </div>
          </div>

          <!-- 快捷操作 -->
          <div class="card">
            <div class="card-header">
              <h3>快捷操作</h3>
            </div>
            <div class="quick-actions">
              <el-button @click="$router.push('/materials')" :icon="Upload" plain class="qa-btn">
                上传简历素材
              </el-button>
              <el-button @click="$router.push('/jd')" :icon="DocumentAdd" plain class="qa-btn">
                添加 JD 解析
              </el-button>
              <el-button @click="$router.push('/resumes')" :icon="Notebook" plain class="qa-btn">
                生成定制简历
              </el-button>
              <el-button @click="$router.push('/delivery')" :icon="Promotion" plain class="qa-btn">
                管理投递任务
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/store'
import { deliveryApi, jdApi, resumeApi, settingsApi } from '@/api/endpoints'
import {
  Upload, DocumentAdd, Notebook, Promotion, DataAnalysis,
  Document, FolderOpened, ChatDotSquare, Connection, Timer
} from '@element-plus/icons-vue'

const router = useRouter()
const appStore = useAppStore()

const loading = ref(false)
const ollamaOnline = ref(false)

const stats = ref({
  jdCount: 0, resumeCount: 0, totalDelivered: 0, replyCount: 0,
})

const recentDeliveries = ref([])
const todayDeliveries = ref(0)
const browserRunning = ref(false)

// ===== 统计卡片配置 =====
const statCards = computed(() => [
  {
    key: 'jd', label: 'JD 总数', value: stats.value.jdCount,
    icon: Document, iconBg: '#EFF6FF', iconColor: '#3B82F6',
  },
  {
    key: 'resume', label: '简历数', value: stats.value.resumeCount,
    icon: FolderOpened, iconBg: '#D1FAE5', iconColor: '#10B981',
  },
  {
    key: 'delivery', label: '累计投递', value: stats.value.totalDelivered,
    icon: Promotion, iconBg: '#FEF3C7', iconColor: '#F59E0B',
  },
  {
    key: 'reply', label: '回复数', value: stats.value.replyCount,
    icon: ChatDotSquare, iconBg: '#EEF2FF', iconColor: '#6366F1',
  },
])

// ===== 新用户判断 =====
const isNewUser = computed(() => {
  return !loading.value && stats.value.jdCount === 0 && stats.value.totalDelivered === 0
})

const hasDeliveryData = computed(() => stats.value.totalDelivered > 0)

// ===== 引导步骤 =====
const guideSteps = [
  { title: '上传简历', desc: '上传你的 PDF/Word 简历，AI 自动解析为结构化素材' },
  { title: '添加目标 JD', desc: '粘贴岗位描述，AI 拆解核心技能要求和权重' },
  { title: '生成定制简历', desc: 'AI 根据 JD 一键生成岗位定制简历和招呼语' },
  { title: '开始投递', desc: '搜索匹配岗位，AI 匹配打分后一键投递' },
]

// ===== 投递漏斗 (演示数据 from stats) =====
const funnelData = computed(() => {
  const s = stats.value
  const max = Math.max(s.totalDelivered, s.replyCount, 1)
  return [
    { key: 'delivered', label: '已投递', value: s.totalDelivered, pct: (s.totalDelivered / max) * 100, color: '#3B82F6' },
    { key: 'replied', label: '已回复', value: s.replyCount, pct: (s.replyCount / max) * 100, color: '#10B981' },
  ]
})

// ===== 状态标签 =====
const statusMap = {
  pending: { label: '待处理', type: 'info' },
  ready: { label: '可投递', type: 'primary' },
  delivered: { label: '已投递', type: 'success' },
  replied: { label: '已回复', type: 'warning' },
  interviewed: { label: '已面试', type: 'success' },
  failed: { label: '失败', type: 'danger' },
}

const statusTagType = (s) => statusMap[s]?.type || 'info'
const statusLabel = (s) => statusMap[s]?.label || s || '-'

const matchScoreField = computed(() => {
  return recentDeliveries.value.some(r => r.match_score !== undefined && r.match_score !== null) ? 'match_score' : ''
})

const matchLevel = (score) => {
  if (!score && score !== 0) return ''
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

// ===== 系统状态 =====
const systemStatus = computed(() => [
  { label: 'LLM 服务', type: 'tag', status: ollamaOnline.value },
  { label: '当前模型', type: 'text', value: appStore.ollamaConfig?.model || '-' },
  { label: '浏览器', type: 'tag', status: browserRunning.value },
  { label: '今日投递', type: 'text', value: `${todayDeliveries.value}/25` },
  { label: '数据库', type: 'tag', status: true },
])

// ===== 数据加载 =====
const loadData = async () => {
  loading.value = true
  try {
    const [jdRes, resumeRes, deliveryRes, statusRes] = await Promise.allSettled([
      jdApi.list({ page: 1, page_size: 1 }),
      resumeApi.list({ page: 1, page_size: 1 }),
      deliveryApi.listJobs({ page: 1, page_size: 100 }),
      deliveryApi.browserStatus(),
    ])

    if (jdRes.status === 'fulfilled') stats.value.jdCount = jdRes.value.pagination?.total || 0
    if (resumeRes.status === 'fulfilled') stats.value.resumeCount = resumeRes.value.pagination?.total || 0
    if (statusRes.status === 'fulfilled') {
      browserRunning.value = statusRes.value.data?.running || false
      todayDeliveries.value = statusRes.value.data?.today_deliveries || 0
    }

    if (deliveryRes.status === 'fulfilled') {
      const all = deliveryRes.value.data || []
      stats.value.totalDelivered = all.filter(j => j.delivery_status === 'delivered').length
      stats.value.replyCount = all.filter(j => j.delivery_status === 'replied' || j.delivery_status === 'interviewed').length
      recentDeliveries.value = all
        .filter(j => j.delivery_status !== 'pending')
        .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
        .slice(0, 10)
    }

    // LLM 状态
    try {
      const cfg = await settingsApi.getLLM()
      if (cfg.code === 200) {
        const p = cfg.data.provider || 'ollama'
        const res = await settingsApi.testLLM({
          provider: p,
          base_url: p === 'deepseek' ? cfg.data.deepseek_base_url : cfg.data.ollama_base_url,
          model: p === 'deepseek' ? cfg.data.deepseek_model : cfg.data.ollama_model,
          api_key: '',
        })
        ollamaOnline.value = res.code === 200
      }
    } catch { /* ignore */ }
  } catch (e) {
    console.error('Dashboard 加载失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
onActivated(loadData)
</script>

<style scoped>
/* ===== 欢迎卡片 ===== */
.welcome-card {
  margin-bottom: 20px;
}

.welcome-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 12px 0;
}

.welcome-icon {
  margin-bottom: 16px;
}

.welcome-content h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.welcome-content > p {
  font-size: 14px;
  color: var(--text-secondary);
  max-width: 480px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.welcome-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  width: 100%;
  max-width: 720px;
  margin-bottom: 28px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: var(--bg-main);
  border-radius: var(--radius-md);
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-align: center;
}

.step-text strong {
  font-size: 13px;
  color: var(--text-primary);
}

.step-text span {
  font-size: 11px;
  color: var(--text-tertiary);
  line-height: 1.4;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

/* ===== 投递漏斗 ===== */
.funnel-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.funnel-item {
  text-align: center;
}

.funnel-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.funnel-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 4px 0 10px;
}

.funnel-bar {
  height: 6px;
  background: var(--bg-main);
  border-radius: 3px;
  overflow: hidden;
}

.funnel-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

/* ===== 岗位单元格 ===== */
.job-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.job-title {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.job-company {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* ===== 匹配度 ===== */
.match-score {
  font-weight: 600;
  font-size: 14px;
}

.match-score.high { color: var(--success); }
.match-score.mid { color: var(--warning); }
.match-score.low { color: var(--danger); }

/* ===== 系统状态 ===== */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
}

.status-row:last-child {
  border-bottom: none;
}

.status-row-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.status-row-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

/* ===== 快捷操作 ===== */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qa-btn {
  justify-content: flex-start !important;
  width: 100%;
  padding: 22px 16px !important;
  font-size: 14px;
  border-radius: var(--radius-md);
}

.qa-btn:hover {
  background: var(--accent-bg) !important;
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .welcome-steps {
    grid-template-columns: repeat(2, 1fr);
  }
  .funnel-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
