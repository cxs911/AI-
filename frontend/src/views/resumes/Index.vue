<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-content">
        <h2>简历管理</h2>
        <div class="subtitle">AI 根据目标 JD 一键生成定制简历和招呼语</div>
      </div>
      <div class="page-actions">
        <el-button @click="showGenerate = true" type="primary" :icon="Plus">生成简历</el-button>
      </div>
    </div>

    <div class="card">
      <el-table :data="resumes" stripe v-loading="loading" style="width:100%">
        <el-table-column label="关联岗位" prop="jd_title" min-width="180">
          <template #default="{ row }">
            <div style="font-weight:500;">{{ row.jd_title || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="公司" prop="jd_company" width="150" />
        <el-table-column label="匹配度" width="90" align="center">
          <template #default="{ row }">
            <span class="match-score" :class="matchLevel(row.match_score)">
              {{ row.match_score || 0 }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'" size="small" effect="plain" round>
              {{ row.status === 'completed' ? '已完成' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="招呼语" width="80">
          <template #default="{ row }">
            <el-tag :type="row.greeting ? 'success' : 'info'" size="small" effect="plain" round>
              {{ row.greeting ? '已生成' : '未生成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="router.push(`/resumes/${row.id}`)">详情</el-button>
            <el-button text size="small" type="primary" @click="exportPdf(row)">导出PDF</el-button>
            <el-popconfirm title="确定删除?" @confirm="deleteResume(row.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!resumes.length && !loading" class="empty-state">
        <el-icon class="empty-icon" :size="36"><Notebook /></el-icon>
        <h4>暂无简历</h4>
        <p>选择已解析的 JD，AI 一键生成针对该岗位的定制简历</p>
        <div class="empty-actions">
          <el-button type="primary" @click="showGenerate = true">生成简历</el-button>
        </div>
      </div>
    </div>

    <!-- 生成简历弹窗 -->
    <el-dialog v-model="showGenerate" title="生成岗位定制简历" width="550px" :close-on-click-modal="false">
      <el-form :model="genForm" label-width="100px">
        <el-form-item label="选择 JD" required>
          <el-select v-model="genForm.jd_id" filterable placeholder="选择岗位JD" style="width:100%;">
            <el-option v-for="jd in jdList" :key="jd.id"
              :label="`${jd.title}${jd.company ? ' - ' + jd.company : ''}`" :value="jd.id" />
          </el-select>
          <div style="font-size:12px; color:var(--text-tertiary); margin-top:4px;">
            需要先添加并解析 JD，才能生成匹配的简历
          </div>
        </el-form-item>
        <el-form-item label="模板风格">
          <el-radio-group v-model="genForm.template_style">
            <el-radio value="professional">专业</el-radio>
            <el-radio value="modern">现代</el-radio>
            <el-radio value="minimal">简约</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerate = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="generateResume">
          {{ generating ? '生成中...' : '开始生成' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { resumeApi, jdApi } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const resumes = ref([])
const jdList = ref([])
const loading = ref(false)
const showGenerate = ref(false)
const generating = ref(false)

const genForm = ref({
  jd_id: null,
  template_style: 'professional',
})

const matchLevel = (score) => {
  if (!score && score !== 0) return ''
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await resumeApi.list()
    resumes.value = res.data || []
    const jdRes = await jdApi.list()
    jdList.value = jdRes.data || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const generateResume = async () => {
  if (!genForm.value.jd_id) {
    ElMessage.warning('请选择JD')
    return
  }
  generating.value = true
  try {
    await resumeApi.generate(genForm.value)
    ElMessage.success('简历生成成功')
    showGenerate.value = false
    loadData()
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.message || ''))
  }
  finally { generating.value = false }
}

const exportPdf = async (row) => {
  try {
    const res = await resumeApi.exportPdf(row.id)
    ElMessage.success('导出成功')
    window.open(res.data?.url, '_blank')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const deleteResume = async (id) => {
  try {
    await resumeApi.delete(id)
    ElMessage.success('已删除')
    loadData()
  } catch (e) { /* ignore */ }
}

onMounted(loadData)
</script>

<style scoped>
.match-score {
  font-weight: 600;
  font-size: 14px;
}
.match-score.high { color: var(--success); }
.match-score.mid { color: var(--warning); }
.match-score.low { color: var(--danger); }
</style>
