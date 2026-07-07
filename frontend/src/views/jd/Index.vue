<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-content">
        <h2>JD智能解析</h2>
        <div class="subtitle">粘贴岗位描述，AI 自动拆解核心技能和权重</div>
      </div>
      <div class="page-actions">
        <el-button @click="showAddDialog = true" type="primary" :icon="Plus">添加 JD</el-button>
      </div>
    </div>

    <div class="card">
      <el-table :data="jdList" stripe v-loading="loading" style="width:100%">
        <el-table-column label="岗位名称" prop="title" min-width="180">
          <template #default="{ row }">
            <div style="font-weight:500;">{{ row.title }}</div>
          </template>
        </el-table-column>
        <el-table-column label="公司" prop="company" width="150" />
        <el-table-column label="城市" prop="city" width="80" />
        <el-table-column label="薪资" width="110">
          <template #default="{ row }">
            <span class="salary-text">{{ row.salary_min ? `${row.salary_min}K-${row.salary_max}K` : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="70">
          <template #default="{ row }">
            <el-tag :type="row.source === 'boss' ? 'primary' : 'info'" size="small" effect="plain" round>
              {{ row.source === 'boss' ? 'Boss' : '手动' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.parsed_result ? 'success' : 'warning'" size="small" effect="plain" round>
              {{ row.parsed_result ? '已解析' : '待解析' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="router.push(`/jd/${row.id}`)">详情</el-button>
            <el-button text size="small" type="primary" :loading="analyzingId === row.id"
              @click="analyzeJD(row)">解析</el-button>
            <el-popconfirm title="确定删除?" @confirm="deleteJD(row.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!jdList.length && !loading" class="empty-state">
        <el-icon class="empty-icon" :size="36"><Document /></el-icon>
        <h4>暂无 JD</h4>
        <p>添加目标岗位描述，AI 将自动拆解核心技能要求和权重</p>
        <div class="empty-actions">
          <el-button type="primary" @click="showAddDialog = true">添加 JD</el-button>
        </div>
      </div>
    </div>

    <!-- 添加JD对话框 -->
    <el-dialog v-model="showAddDialog" title="添加 JD" width="640px" :close-on-click-modal="false">
      <el-form :model="jdForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="岗位名称" required>
              <el-input v-model="jdForm.title" placeholder="如：Python后端开发" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="公司名称">
              <el-input v-model="jdForm.company" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="城市">
              <el-input v-model="jdForm.city" placeholder="如：北京" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="薪资范围">
              <div style="display:flex;align-items:center;gap:4px;">
                <el-input-number v-model="jdForm.salary_min" :min="0" :max="200" size="small" controls-position="right" style="width:100px;" />
                <span style="color:var(--text-tertiary);">~</span>
                <el-input-number v-model="jdForm.salary_max" :min="0" :max="200" size="small" controls-position="right" style="width:100px;" />
                <span style="color:var(--text-tertiary);margin-left:2px;">K</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="JD 全文" required>
          <el-input v-model="jdForm.raw_content" type="textarea" :rows="10"
            placeholder="粘贴完整的岗位描述（JD）全文..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveJD">保存并解析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { jdApi } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const jdList = ref([])
const loading = ref(false)
const saving = ref(false)
const analyzingId = ref(null)
const showAddDialog = ref(false)

const jdForm = ref({
  title: '', company: '', city: '',
  salary_min: 0, salary_max: 0,
  raw_content: '',
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await jdApi.list()
    jdList.value = res.data || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const saveJD = async () => {
  if (!jdForm.value.title || !jdForm.value.raw_content) {
    ElMessage.warning('请填写岗位名称和JD内容')
    return
  }
  saving.value = true
  try {
    await jdApi.create(jdForm.value)
    ElMessage.success('保存成功')
    showAddDialog.value = false
    jdForm.value = { title: '', company: '', city: '', salary_min: 0, salary_max: 0, raw_content: '' }
    loadData()
  } catch (e) { console.error(e) }
  finally { saving.value = false }
}

const analyzeJD = async (row) => {
  analyzingId.value = row.id
  try {
    await jdApi.analyze(row.id)
    ElMessage.success('解析完成')
    loadData()
  } catch (e) {
    ElMessage.error('解析失败: ' + (e.message || '未知错误'))
  }
  finally { analyzingId.value = null }
}

const deleteJD = async (id) => {
  try {
    await jdApi.delete(id)
    ElMessage.success('已删除')
    loadData()
  } catch (e) { /* ignore */ }
}

onMounted(loadData)
</script>

<style scoped>
.salary-text {
  font-weight: 500;
  color: var(--text-primary);
}
</style>
