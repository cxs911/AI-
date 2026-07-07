<template>
  <div class="page-container">
    <el-button @click="router.back()" :icon="ArrowLeft" style="margin-bottom: 16px;" text>返回列表</el-button>

    <div v-if="resume">
      <el-row :gutter="20">
        <!-- 简历预览 -->
        <el-col :xs="24" :lg="16">
          <div class="card">
            <div class="card-header">
              <h3>简历预览</h3>
              <div style="display:flex; gap:8px;">
                <el-button size="small" :icon="View" @click="showPreview = true">实时预览</el-button>
                <el-button size="small" :icon="Download" @click="exportPdf">导出 PDF</el-button>
              </div>
            </div>

            <div class="resume-content">
              <div class="resume-header">
                <h2>{{ resume.personal_info?.name || '个人信息' }}</h2>
                <div class="contact-info">
                  <span v-if="resume.personal_info?.phone">📞 {{ resume.personal_info.phone }}</span>
                  <span v-if="resume.personal_info?.email">✉️ {{ resume.personal_info.email }}</span>
                  <span v-if="resume.personal_info?.location">📍 {{ resume.personal_info.location }}</span>
                </div>
              </div>

              <!-- 匹配度 -->
              <div v-if="resume.match_score" class="match-banner" :class="matchBannerClass">
                <div class="match-banner-score">{{ resume.match_score }}%</div>
                <div class="match-banner-info">
                  <strong>岗位匹配度</strong>
                  <span>{{ matchBannerText }}</span>
                </div>
              </div>

              <!-- 个人总结 -->
              <div v-if="resume.summary" class="section">
                <h3>个人总结</h3>
                <p>{{ resume.summary }}</p>
              </div>

              <!-- 技能 -->
              <div v-if="resume.skills?.length" class="section">
                <h3>技能</h3>
                <div class="skills-tags">
                  <el-tag v-for="s in resume.skills" :key="s" size="small" effect="plain" style="margin:3px;">{{ s }}</el-tag>
                </div>
              </div>

              <!-- 工作经历 -->
              <div v-if="resume.work_experience?.length" class="section">
                <h3>工作经历</h3>
                <div v-for="(exp, i) in resume.work_experience" :key="i" class="exp-item">
                  <div class="exp-header">
                    <strong>{{ exp.title || exp.company || '' }}</strong>
                    <span class="exp-date">{{ exp.start_date || '' }} - {{ exp.end_date || '' }}</span>
                  </div>
                  <p>{{ exp.description || '' }}</p>
                  <div v-if="exp.relevance" class="exp-relevance">🎯 {{ exp.relevance }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右侧操作区 -->
        <el-col :xs="24" :lg="8">
          <!-- 招呼语 -->
          <div class="card" style="margin-bottom:20px;">
            <div class="card-header">
              <h3>招呼语</h3>
            </div>
            <div v-if="resume.greeting" class="greeting-box">
              <p>{{ resume.greeting }}</p>
            </div>
            <div v-else class="greeting-empty">
              <el-icon :size="28" color="var(--text-tertiary)"><ChatDotSquare /></el-icon>
              <p>未生成招呼语</p>
            </div>
            <el-divider style="margin:12px 0;" />
            <el-select v-model="greetingStyle" size="small" style="width:100%;">
              <el-option label="应届生风格" value="fresh" />
              <el-option label="社招风格" value="social" />
            </el-select>
            <el-button type="primary" style="width:100%; margin-top: 8px;"
              :loading="genGreeting" @click="generateGreeting">
              <el-icon><MagicStick /></el-icon> {{ genGreeting ? '生成中...' : '生成招呼语' }}
            </el-button>
          </div>

          <!-- 岗位匹配信息 -->
          <div class="card">
            <div class="card-header">
              <h3>岗位信息</h3>
            </div>
            <div class="match-info">
              <div class="mi-item">
                <span class="mi-label">岗位</span>
                <span class="mi-value">{{ resume.jd_title || '-' }}</span>
              </div>
              <div class="mi-item">
                <span class="mi-label">公司</span>
                <span class="mi-value">{{ resume.jd_company || '-' }}</span>
              </div>
              <div class="mi-item">
                <span class="mi-label">状态</span>
                <el-tag :type="resume.status === 'completed' ? 'success' : 'info'" size="small" effect="plain" round>
                  {{ resume.status === 'completed' ? '已完成' : '草稿' }}
                </el-tag>
              </div>
              <div class="mi-item">
                <span class="mi-label">模板</span>
                <span class="mi-value">{{ resume.template_style || 'professional' }}</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 预览弹窗 -->
    <el-dialog v-model="showPreview" title="简历预览" width="800px" fullscreen>
      <iframe :srcdoc="previewHtml" style="width:100%; height:80vh; border:none;" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { resumeApi } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import { ArrowLeft, View, Download, ChatDotSquare, MagicStick } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const resume = ref(null)
const showPreview = ref(false)
const previewHtml = ref('')
const genGreeting = ref(false)
const greetingStyle = ref('fresh')

const matchBannerClass = computed(() => {
  const s = resume.value?.match_score
  if (!s) return ''
  if (s >= 80) return 'high'
  if (s >= 60) return 'mid'
  return 'low'
})

const matchBannerText = computed(() => {
  const s = resume.value?.match_score
  if (!s) return ''
  if (s >= 80) return '高度匹配，推荐优先投递'
  if (s >= 60) return '部分匹配，可以尝试投递'
  return '匹配度较低，建议优化简历'
})

const loadResume = async () => {
  try {
    const res = await resumeApi.get(route.params.id)
    resume.value = res.data
  } catch (e) {
    ElMessage.error('加载简历失败')
    router.push('/resumes')
  }
}

const exportPdf = async () => {
  try {
    const res = await resumeApi.exportPdf(resume.value.id)
    ElMessage.success('导出成功')
    if (res.data?.url) window.open(res.data.url, '_blank')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const generateGreeting = async () => {
  genGreeting.value = true
  try {
    const res = await resumeApi.greeting(resume.value.id, { style: greetingStyle.value })
    resume.value.greeting = res.data?.greeting
    ElMessage.success('招呼语生成成功')
  } catch (e) {
    ElMessage.error('生成失败')
  }
  finally { genGreeting.value = false }
}

onMounted(loadResume)
</script>

<style scoped>
.resume-content {
  max-width: 800px;
}

.resume-header {
  text-align: center;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--primary);
  margin-bottom: 16px;
}

.resume-header h2 {
  font-size: 24px;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.contact-info {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 13px;
  color: var(--text-secondary);
}

/* 匹配度横幅 */
.match-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
}

.match-banner.high {
  background: var(--success-bg);
}

.match-banner.mid {
  background: var(--warning-bg);
}

.match-banner.low {
  background: var(--danger-bg);
}

.match-banner-score {
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.match-banner.high .match-banner-score { color: var(--success); }
.match-banner.mid .match-banner-score { color: var(--warning); }
.match-banner.low .match-banner-score { color: var(--danger); }

.match-banner-info {
  display: flex;
  flex-direction: column;
}

.match-banner-info strong {
  font-size: 14px;
  color: var(--text-primary);
}

.match-banner-info span {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 内容章节 */
.section {
  margin-bottom: 20px;
}

.section h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 6px;
  margin-bottom: 10px;
}

.section p {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
}

.exp-item {
  margin-bottom: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-light);
}

.exp-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.exp-header strong {
  font-size: 14px;
  color: var(--text-primary);
}

.exp-date {
  color: var(--text-tertiary);
  font-size: 13px;
}

.exp-relevance {
  font-size: 12px;
  color: var(--accent);
  margin-top: 4px;
}

/* 右侧 */
.greeting-box {
  background: var(--bg-main);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
}

.greeting-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px;
  color: var(--text-tertiary);
  font-size: 13px;
}

.match-info {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.mi-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
}

.mi-item:last-child {
  border-bottom: none;
}

.mi-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.mi-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}
</style>
