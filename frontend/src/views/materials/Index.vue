<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-content">
        <h2>个人素材库</h2>
        <div class="subtitle">管理你的简历文件、STAR 经历库</div>
      </div>
      <div class="page-actions">
        <el-button @click="activeTab = 'experience'" :icon="EditPen" plain>管理经历</el-button>
        <el-button @click="showUpload = true" type="primary" :icon="Upload">上传简历</el-button>
      </div>
    </div>

    <!-- 标签 -->
    <div class="card" style="padding: 12px 20px; margin-bottom: 20px;">
      <span style="font-size:13px; color: var(--text-secondary); margin-right: 12px;">筛选：</span>
      <el-tag
        :type="tagFilter === '' ? 'primary' : 'info'"
        style="cursor:pointer; margin: 4px;"
        @click="tagFilter = ''"
        effect="plain"
        round
      >全部</el-tag>
      <el-tag
        v-for="tag in tags" :key="tag.id"
        style="cursor:pointer; margin: 4px;"
        :type="tagFilter === tag.name ? 'primary' : 'info'"
        effect="plain"
        round
        @click="tagFilter = tag.name"
      >{{ tag.name }}</el-tag>
    </div>

    <el-tabs v-model="activeTab">
      <!-- 素材列表 -->
      <el-tab-pane label="简历素材" name="material">
        <el-table :data="materials" stripe v-loading="loading">
          <el-table-column label="标题" prop="title" min-width="180" />
          <el-table-column label="类型" width="80">
            <template #default="{ row }">{{ row.file_type?.toUpperCase() }}</template>
          </el-table-column>
          <el-table-column label="分类" width="100">
            <template #default="{ row }">{{ row.category }}</template>
          </el-table-column>
          <el-table-column label="标签" min-width="200">
            <template #default="{ row }">
              <el-tag v-for="t in row.tags" :key="t.id" size="small" style="margin: 2px;">{{ t.name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="上传时间" width="170" prop="created_at" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click="viewMaterial(row)">查看</el-button>
              <el-popconfirm title="确定删除?" @confirm="deleteMaterial(row.id)">
                <template #reference>
                  <el-button text type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="!materials.length && !loading" class="empty-state">
          <el-icon class="empty-icon"><FolderOpened /></el-icon>
          <h4>暂无素材</h4>
          <p>上传你的简历文件，AI 会自动解析为结构化素材</p>
          <div class="empty-actions">
            <el-button type="primary" @click="showUpload = true">上传简历</el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- 经历管理 -->
      <el-tab-pane label="经历库" name="experience">
        <div style="margin-bottom: 16px;">
          <el-button @click="showExpDialog = true" type="primary" :icon="Plus" size="small">添加经历</el-button>
        </div>
        <el-table :data="experiences" stripe v-loading="expLoading">
          <el-table-column label="标题" prop="title" min-width="160" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="expTypeMap[row.category]?.type">{{ expTypeMap[row.category]?.label }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="组织/公司" prop="organization" width="150" />
          <el-table-column label="角色" prop="role" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.star_desc ? 'success' : 'warning'" size="small">
                {{ row.star_desc ? '已优化' : '待优化' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click="optimizeExp(row)">AI优化</el-button>
              <el-popconfirm title="确定删除?" @confirm="deleteExp(row.id)">
                <template #reference>
                  <el-button text type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="!experiences.length && !expLoading" class="empty-state">
          <el-icon class="empty-icon"><EditPen /></el-icon>
          <h4>暂无经历</h4>
          <p>添加你的项目、实习或工作经历，AI 会自动转化为 STAR 量化描述</p>
          <div class="empty-actions">
            <el-button type="primary" @click="showExpDialog = true">添加经历</el-button>
          </div>
        </div>
        </el-tab-pane>
    </el-tabs>

    <!-- 上传弹窗 -->
    <el-dialog v-model="showUpload" title="上传简历" width="500px">
      <el-upload
        drag
        accept=".pdf,.doc,.docx,.txt"
        :auto-upload="false"
        :limit="1"
        ref="uploadRef"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload" :size="48"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或<em>点击选择</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF / Word / TXT 格式</div>
        </template>
      </el-upload>
      <div style="margin-top: 16px;">
        <el-input v-model="uploadTitle" placeholder="素材标题" />
      </div>
      <div style="margin-top: 12px;">
        <el-select v-model="uploadCategory" placeholder="选择分类" style="width: 100%;">
          <el-option label="简历" value="resume" />
          <el-option label="证书" value="certificate" />
          <el-option label="作品" value="portfolio" />
          <el-option label="通用" value="general" />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="confirmUpload">上传并解析</el-button>
      </template>
    </el-dialog>

    <!-- 经历编辑弹窗 -->
    <el-dialog v-model="showExpDialog" title="添加经历" width="600px">
      <el-form :model="expForm" label-width="100px">
        <el-form-item label="经历标题" required>
          <el-input v-model="expForm.title" placeholder="如：XX项目开发" />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="expForm.category">
            <el-option label="课程项目" value="course" />
            <el-option label="校园经历" value="school" />
            <el-option label="工作经历" value="work" />
            <el-option label="实习经历" value="intern" />
            <el-option label="项目实践" value="project" />
          </el-select>
        </el-form-item>
        <el-form-item label="组织/公司">
          <el-input v-model="expForm.organization" placeholder="学校/公司名称" />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-input v-model="expForm.start_date" placeholder="开始时间" style="width: 45%;" />
          <span style="margin: 0 8px;">至</span>
          <el-input v-model="expForm.end_date" placeholder="结束时间" style="width: 45%;" />
        </el-form-item>
        <el-form-item label="角色/职位">
          <el-input v-model="expForm.role" placeholder="如：项目组长" />
        </el-form-item>
        <el-form-item label="原始描述" required>
          <el-input v-model="expForm.original_desc" type="textarea" :rows="4"
            placeholder="请详细描述你做了什么，后续AI会转化为STAR量化表述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExpDialog = false">取消</el-button>
        <el-button type="primary" @click="saveExperience">保存</el-button>
      </template>
    </el-dialog>

    <!-- 素材预览 -->
    <el-dialog v-model="showPreview" title="素材详情" width="700px">
      <div v-if="currentMaterial">
        <h3 style="margin-bottom: 12px;">{{ currentMaterial.title }}</h3>
        <el-tag size="small" style="margin-bottom: 12px;">{{ currentMaterial.file_type?.toUpperCase() }}</el-tag>
        <el-divider />
        <pre class="preview-text">{{ currentMaterial.raw_text?.slice(0, 3000) }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { materialApi } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import { Upload, EditPen, Plus, UploadFilled } from '@element-plus/icons-vue'

const activeTab = ref('material')
const loading = ref(false)
const expLoading = ref(false)
const materials = ref([])
const experiences = ref([])
const tags = ref([])
const tagFilter = ref('')

// 上传
const showUpload = ref(false)
const uploading = ref(false)
const uploadFile = ref(null)
const uploadTitle = ref('')
const uploadCategory = ref('general')
const uploadRef = ref(null)

// 经历弹窗
const showExpDialog = ref(false)
const showPreview = ref(false)
const currentMaterial = ref(null)

const expForm = ref({
  title: '', category: 'work', organization: '',
  start_date: '', end_date: '', role: '', original_desc: '',
})

const expTypeMap = {
  work: { label: '工作', type: 'primary' },
  intern: { label: '实习', type: 'success' },
  school: { label: '校园', type: 'warning' },
  course: { label: '课程', type: 'info' },
  project: { label: '项目', type: '' },
}

const loadMaterials = async () => {
  loading.value = true
  try {
    const res = await materialApi.list({ tag: tagFilter.value || undefined })
    materials.value = res.data || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const loadExperiences = async () => {
  expLoading.value = true
  try {
    const res = await materialApi.listExperiences()
    experiences.value = res.data || []
  } catch (e) { console.error(e) }
  finally { expLoading.value = false }
}

const loadTags = async () => {
  try {
    const res = await materialApi.listTags()
    tags.value = res.data || []
  } catch (e) { /* ignore */ }
}

watch(tagFilter, () => loadMaterials())

const handleFileChange = (file) => {
  uploadFile.value = file.raw
  if (!uploadTitle.value) {
    uploadTitle.value = file.name.replace(/\.[^.]+$/, '')
  }
}

const confirmUpload = async () => {
  if (!uploadFile.value) { ElMessage.warning('请选择文件'); return }
  if (!uploadTitle.value) { ElMessage.warning('请输入标题'); return }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    formData.append('title', uploadTitle.value)
    formData.append('category', uploadCategory.value)
    formData.append('tags', '[]')
    await materialApi.upload(formData)
    ElMessage.success('上传并解析成功')
    showUpload.value = false
    loadMaterials()
    uploadFile.value = null
    uploadTitle.value = ''
  } catch (e) { console.error(e) }
  finally { uploading.value = false }
}

const deleteMaterial = async (id) => {
  try {
    await materialApi.delete(id)
    ElMessage.success('已删除')
    loadMaterials()
  } catch (e) { /* ignore */ }
}

const viewMaterial = async (row) => {
  try {
    const res = await materialApi.get(row.id)
    currentMaterial.value = res.data
    showPreview.value = true
  } catch (e) { /* ignore */ }
}

const saveExperience = async () => {
  try {
    await materialApi.createExperience(expForm.value)
    ElMessage.success('经历已保存')
    showExpDialog.value = false
    expForm.value = { title: '', category: 'work', organization: '', start_date: '', end_date: '', role: '', original_desc: '' }
    loadExperiences()
  } catch (e) { /* ignore */ }
}

const optimizeExp = async (row) => {
  try {
    const res = await materialApi.optimizeExperience(row.id, { jd_keywords: '[]' })
    ElMessage.success('AI优化完成')
    loadExperiences()
  } catch (e) { /* ignore */ }
}

const deleteExp = async (id) => {
  try {
    await materialApi.deleteExperience(id)
    ElMessage.success('已删除')
    loadExperiences()
  } catch (e) { /* ignore */ }
}

onMounted(() => {
  loadMaterials()
  loadExperiences()
  loadTags()
})
</script>

<style scoped>
.preview-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 13px;
  line-height: 1.6;
  max-height: 500px;
  overflow-y: auto;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}
</style>
