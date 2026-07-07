<template>
  <div class="page-container">
    <!-- ===== 页面标题 ===== -->
    <div class="page-header">
      <div class="page-header-content">
        <h2>投递管理</h2>
        <div class="subtitle">搜索岗位、AI 匹配、一键投递</div>
      </div>
      <div class="page-actions">
        <el-button size="small" :icon="Refresh" @click="refreshJobs">刷新列表</el-button>
      </div>
    </div>

    <!-- ===== 浏览器控制栏 ===== -->
    <div class="card browser-card" style="margin-bottom: 20px;">
      <div class="browser-bar">
        <div class="browser-left">
          <div class="browser-indicator">
            <span class="indicator-dot" :class="browserRunning ? 'active' : ''"></span>
            <span>浏览器</span>
            <el-tag v-if="browserRunning" size="small" type="success" effect="plain" round>运行中</el-tag>
            <el-tag v-else size="small" type="info" effect="plain" round>未启动</el-tag>
            <el-tag v-if="isPaused" size="small" type="danger" effect="dark" round style="margin-left:4px;">
              已暂停(人机验证)
            </el-tag>
          </div>
          <div class="browser-meta">
            <span>今日投递: <strong>{{ todayDeliveries }}/25</strong></span>
          </div>
        </div>
        <div class="browser-right">
          <el-button size="small" @click="startBrowser" :loading="browserLoading" type="primary">
            <template v-if="!browserRunning">启动浏览器</template>
            <template v-else>重启浏览器</template>
          </el-button>
          <el-button size="small" @click="closeBrowser" :disabled="!browserRunning">关闭</el-button>
          <el-switch
            v-model="manualReview"
            active-text="人工审核"
            inactive-text="自动模式"
            style="margin-left: 8px;"
          />
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- ===== 左栏：搜索 + 列表 ===== -->
      <el-col :xs="24" :lg="16">
        <!-- 搜索 -->
        <div class="card" style="margin-bottom: 20px;">
          <el-form :model="searchForm" inline>
            <el-form-item label="关键词">
              <el-input v-model="searchForm.keywords" placeholder="如：Python开发" clearable style="width:160px;" />
            </el-form-item>
            <el-form-item label="城市">
              <el-input v-model="searchForm.city" style="width:90px;" clearable />
            </el-form-item>
            <el-form-item label="薪资">
              <el-input-number v-model="searchForm.salary_min" :min="0" :max="200" size="small" controls-position="right" style="width:100px;" />
              <span style="margin: 0 6px; color: var(--text-tertiary);">-</span>
              <el-input-number v-model="searchForm.salary_max" :min="0" :max="200" size="small" controls-position="right" style="width:100px;" />
              <span style="margin-left: 4px; color: var(--text-tertiary);">K</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="searchJobs" :loading="searching">
                <el-icon><Search /></el-icon> 搜索岗位
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 岗位列表 -->
        <div class="card">
          <div class="card-header">
            <h3>匹配岗位列表</h3>
            <div style="display:flex; gap:8px; align-items:center;">
              <span v-if="selectedJobs.length" style="font-size:13px; color:var(--text-tertiary);">
                已选 {{ selectedJobs.length }} 个
              </span>
              <el-button size="small" type="primary" @click="batchDeliver"
                :disabled="!selectedJobs.length || !manualReview">
                <el-icon><Promotion /></el-icon> 批量投递
              </el-button>
            </div>
          </div>
          <el-table :data="jobs" stripe v-loading="loading" @selection-change="onSelectChange" style="width:100%">
            <el-table-column type="selection" width="40" />
            <el-table-column label="岗位" min-width="180">
              <template #default="{ row }">
                <div class="job-cell">
                  <span class="job-title">{{ row.title }}</span>
                  <span class="job-company">{{ row.company }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="城市" width="70" prop="city" />
            <el-table-column label="薪资" width="110">
              <template #default="{ row }">
                <span class="salary-text">{{ row.salary_str || (row.salary_min ? `${row.salary_min}K-${row.salary_max}K` : '-') }}</span>
              </template>
            </el-table-column>
            <el-table-column label="匹配度" width="80" align="center">
              <template #default="{ row }">
                <span class="match-score" :class="matchLevel(row.match_score)">{{ row.match_score || '-' }}{{ row.match_score ? '%' : '' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.delivery_status)" size="small" effect="plain" round>
                  {{ statusLabel(row.delivery_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="130" fixed="right">
              <template #default="{ row }">
                <el-button text size="small" type="primary" @click="deliverSingle(row)"
                  :disabled="row.delivery_status === 'delivered' || !browserRunning">
                  投递
                </el-button>
                <el-button text size="small" @click="showGreeting(row)">话术</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="!jobs.length && !loading" class="empty-state">
            <el-icon class="empty-icon" :size="36"><Promotion /></el-icon>
            <h4>暂无岗位</h4>
            <p>设置搜索条件后点击「搜索岗位」从 Boss 直聘获取匹配岗位</p>
          </div>
        </div>
      </el-col>

      <!-- ===== 右栏：统计 + 信息 ===== -->
      <el-col :xs="24" :lg="8">
        <div class="card" style="margin-bottom: 20px;">
          <div class="card-header">
            <h3>投递统计</h3>
          </div>
          <div class="delivery-stats">
            <div class="ds-item">
              <div class="ds-value">{{ totalJobs }}</div>
              <div class="ds-label">总岗位数</div>
            </div>
            <div class="ds-item">
              <div class="ds-value" style="color: var(--success);">{{ totalDelivered }}</div>
              <div class="ds-label">已投递</div>
            </div>
            <div class="ds-item">
              <div class="ds-value" style="color: var(--warning);">{{ totalReplied }}</div>
              <div class="ds-label">已回复</div>
            </div>
            <div class="ds-item">
              <div class="ds-value" style="color: var(--danger);">{{ totalFailed }}</div>
              <div class="ds-label">失败</div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>投递建议</h3>
          </div>
          <div class="tip-list">
            <div class="tip-item">
              <el-icon color="#3B82F6"><InfoFilled /></el-icon>
              <span>建议在工作日 9:00-18:00 投递</span>
            </div>
            <div class="tip-item">
              <el-icon color="#10B981"><SuccessFilled /></el-icon>
              <span>匹配度 &gt;80% 的岗位优先投递</span>
            </div>
            <div class="tip-item">
              <el-icon color="#F59E0B"><WarningFilled /></el-icon>
              <span>每日投递上限 {{ deliveryLimit }} 个</span>
            </div>
            <div class="tip-item">
              <el-icon color="#6366F1"><Connection /></el-icon>
              <span>每次投递间隔 {{ minInterval }}-{{ maxInterval }} 秒</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 招呼语编辑弹窗 -->
    <el-dialog v-model="showGreetingDialog" title="编辑招呼语" width="520px" :close-on-click-modal="false">
      <div style="margin-bottom:12px; font-size:13px; color:var(--text-secondary);">
        自定义投递时发送的招呼语，AI 会根据岗位信息生成
      </div>
      <el-input v-model="editingGreeting" type="textarea" :rows="5" placeholder="请输入招呼语..." />
      <div style="margin-top:12px; text-align:right;">
        <el-button size="small" @click="autoGenerateGreeting" :loading="generating">
          <el-icon><MagicStick /></el-icon> AI 生成
        </el-button>
      </div>
      <template #footer>
        <el-button @click="showGreetingDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGreeting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { deliveryApi, jdApi, settingsApi } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import {
  Refresh, Promotion, Search, InfoFilled,
  SuccessFilled, WarningFilled, Connection, MagicStick
} from '@element-plus/icons-vue'

const loading = ref(false)
const searching = ref(false)
const browserLoading = ref(false)
const browserRunning = ref(false)
const isPaused = ref(false)
const todayDeliveries = ref(0)
const manualReview = ref(false)
const jobs = ref([])
const selectedJobs = ref([])
const showGreetingDialog = ref(false)
const editingGreeting = ref('')
const editingJob = ref(null)
const generating = ref(false)
const deliveryLimit = ref(25)
const minInterval = ref(15)
const maxInterval = ref(40)

const searchForm = ref({
  keywords: 'Python',
  city: '北京',
  salary_min: 0,
  salary_max: 100,
})

// ===== 统计 =====
const totalJobs = computed(() => jobs.value.length)
const totalDelivered = computed(() => jobs.value.filter(j => j.delivery_status === 'delivered').length)
const totalReplied = computed(() => jobs.value.filter(j => j.delivery_status === 'replied' || j.delivery_status === 'interviewed').length)
const totalFailed = computed(() => jobs.value.filter(j => j.delivery_status === 'failed').length)

// ===== 状态映射 =====
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

const matchLevel = (score) => {
  if (!score && score !== 0) return ''
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

// ===== 方法 =====
const checkBrowserStatus = async () => {
  try {
    const res = await deliveryApi.browserStatus()
    browserRunning.value = res.data?.running || false
    isPaused.value = res.data?.paused || false
    todayDeliveries.value = res.data?.today_deliveries || 0
  } catch { /* ignore */ }
}

const startBrowser = async () => {
  browserLoading.value = true
  try {
    await deliveryApi.startBrowser()
    ElMessage.success('浏览器已启动')
    browserRunning.value = true
    setTimeout(async () => {
      try {
        await deliveryApi.waitLogin({ timeout: 120 })
        ElMessage.success('登录成功')
        checkBrowserStatus()
      } catch {
        ElMessage.warning('登录超时，请在浏览器中完成扫码')
      }
    }, 2000)
  } catch {
    ElMessage.error('浏览器启动失败')
  } finally {
    browserLoading.value = false
  }
}

const closeBrowser = async () => {
  try {
    await deliveryApi.closeBrowser()
    browserRunning.value = false
    ElMessage.success('浏览器已关闭')
  } catch { /* ignore */ }
}

const searchJobs = async () => {
  searching.value = true
  try {
    const res = await deliveryApi.searchJobs(searchForm.value)
    ElMessage.success(`搜索到 ${res.data?.total || 0} 个岗位，新增 ${res.data?.saved || 0} 个`)
    await refreshJobs()
  } catch {
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
  }
}

const refreshJobs = async () => {
  loading.value = true
  try {
    const res = await deliveryApi.listJobs()
    jobs.value = res.data || []
  } catch { /* ignore */ }
  finally { loading.value = false }
}

const onSelectChange = (selection) => {
  selectedJobs.value = selection
}

const deliverSingle = async (row) => {
  try {
    await deliveryApi.deliverSingle(row.id)
    ElMessage.success('投递成功')
    checkBrowserStatus()
    refreshJobs()
  } catch {
    ElMessage.error('投递失败')
  }
}

const batchDeliver = async () => {
  if (!selectedJobs.value.length) return
  if (!manualReview.value) {
    ElMessage.warning('请开启人工审核开关')
    return
  }
  try {
    const ids = selectedJobs.value.map(j => j.id)
    const res = await deliveryApi.deliverBatch({ job_ids: ids, enable_review: manualReview.value })
    ElMessage.success(`批量投递完成: 成功${res.data?.success || 0}个`)
    checkBrowserStatus()
    refreshJobs()
  } catch {
    ElMessage.error('批量投递失败')
  }
}

const showGreeting = (row) => {
  editingJob.value = row
  editingGreeting.value = row.greeting || ''
  showGreetingDialog.value = true
}

const autoGenerateGreeting = async () => {
  if (!editingJob.value) return
  generating.value = true
  try {
    const res = await jdApi.generateGreeting(editingJob.value.id, { style: 'fresh' })
    if (res.code === 200) {
      editingGreeting.value = res.data?.greeting || editingGreeting.value
      ElMessage.success('AI 招呼语生成成功')
    }
  } catch {
    ElMessage.warning('AI 生成失败，请手动编辑')
  } finally {
    generating.value = false
  }
}

const saveGreeting = async () => {
  ElMessage.success('招呼语已保存（本地）')
  if (editingJob.value) editingJob.value.greeting = editingGreeting.value
  showGreetingDialog.value = false
}

// ===== 加载系统配置 =====
const loadConfig = async () => {
  try {
    const res = await settingsApi.getSystem()
    if (res.code === 200) {
      deliveryLimit.value = res.data?.delivery_limit || 25
    }
  } catch { /* ignore */ }
}

onMounted(() => {
  checkBrowserStatus()
  refreshJobs()
  loadConfig()
})
</script>

<style scoped>
.browser-card {
  padding: 16px 20px;
}

.browser-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.browser-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.browser-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  position: relative;
}

.indicator-dot.active {
  background: var(--success);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.browser-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

.browser-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 岗位列表 */
.job-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.job-title { font-weight: 500; font-size: 14px; color: var(--text-primary); }
.job-company { font-size: 12px; color: var(--text-tertiary); }

.salary-text {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.match-score {
  font-weight: 600;
  font-size: 14px;
}
.match-score.high { color: var(--success); }
.match-score.mid { color: var(--warning); }
.match-score.low { color: var(--danger); }

/* 投递统计 */
.delivery-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.ds-item {
  text-align: center;
}

.ds-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.ds-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 投递建议 */
.tip-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.tip-item .el-icon {
  margin-top: 1px;
  flex-shrink: 0;
}
</style>
