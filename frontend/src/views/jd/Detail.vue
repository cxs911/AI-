<template>
  <div class="page-container">
    <el-button @click="router.back()" :icon="ArrowLeft" style="margin-bottom: 16px;" text>返回列表</el-button>

    <div v-if="jd" class="jd-detail">
      <el-row :gutter="20">
        <!-- JD 基本信息 -->
        <el-col :xs="24" :lg="16">
          <div class="card">
            <div class="card-header">
              <h3>{{ jd.title }}</h3>
              <el-tag :type="jd.source === 'boss' ? 'primary' : 'info'" size="small" effect="plain" round>
                {{ jd.source === 'boss' ? 'Boss直聘' : '手动添加' }}
              </el-tag>
            </div>
            <div class="jd-info-grid">
              <div class="jd-info-item" v-if="jd.company">
                <span class="jd-info-label">公司</span>
                <span class="jd-info-value">{{ jd.company }}</span>
              </div>
              <div class="jd-info-item" v-if="jd.city">
                <span class="jd-info-label">城市</span>
                <span class="jd-info-value">{{ jd.city }}</span>
              </div>
              <div class="jd-info-item" v-if="jd.salary_min">
                <span class="jd-info-label">薪资</span>
                <span class="jd-info-value">{{ jd.salary_min }}K - {{ jd.salary_max }}K</span>
              </div>
              <div class="jd-info-item" v-if="jd.experience">
                <span class="jd-info-label">经验</span>
                <span class="jd-info-value">{{ jd.experience }}</span>
              </div>
              <div class="jd-info-item" v-if="jd.education">
                <span class="jd-info-label">学历</span>
                <span class="jd-info-value">{{ jd.education }}</span>
              </div>
              <div class="jd-info-item">
                <span class="jd-info-label">创建时间</span>
                <span class="jd-info-value">{{ jd.created_at }}</span>
              </div>
            </div>
            <el-divider />
            <h4 style="margin-bottom: 10px; font-size:15px; font-weight:600;">JD 原文</h4>
            <pre class="jd-content">{{ jd.raw_content }}</pre>
          </div>
        </el-col>

        <!-- AI 解析结果 -->
        <el-col :xs="24" :lg="8">
          <div class="card" style="position:sticky; top:20px;">
            <div class="card-header">
              <h3>AI 解析结果</h3>
            </div>

            <div v-if="parsed">
              <!-- 综合评分 -->
              <div class="score-section">
                <el-progress type="circle" :percentage="parsed.total_score || 0" :width="100" :stroke-width="8"
                  :color="parsed.total_score >= 80 ? 'var(--success)' : parsed.total_score >= 60 ? 'var(--warning)' : 'var(--danger)'" />
                <div class="score-label">综合能力评分</div>
              </div>

              <el-divider />
              <h4 class="section-title">核心技能要求</h4>
              <div v-for="skill in parsed.core_skills" :key="skill.name" class="skill-item">
                <div class="skill-header">
                  <span>{{ skill.name }}</span>
                  <el-tag size="small" :type="skill.have_gap ? 'danger' : 'success'" effect="plain" round>
                    {{ skill.level }}
                  </el-tag>
                </div>
                <el-progress :percentage="skill.weight" :stroke-width="6"
                  :color="skill.have_gap ? 'var(--danger)' : 'var(--accent)'" />
                <div v-if="skill.have_gap" class="gap-tip">⚠ {{ skill.gap_description || '可能存在能力缺口' }}</div>
              </div>

              <el-divider v-if="parsed.soft_skills?.length" />
              <h4 v-if="parsed.soft_skills?.length" class="section-title">软性能力</h4>
              <div v-if="parsed.soft_skills?.length" class="soft-skills">
                <el-tag v-for="s in parsed.soft_skills" :key="s.name" size="small" effect="plain" round style="margin:3px;">
                  {{ s.name }}
                </el-tag>
              </div>

              <el-divider />
              <h4 class="section-title">关键词</h4>
              <div class="keywords">
                <el-tag v-for="kw in parsed.keywords" :key="kw" size="small" effect="plain" style="margin:3px;">{{ kw }}</el-tag>
              </div>
            </div>

            <div v-else class="unparsed-state">
              <el-icon :size="40" color="var(--text-tertiary)"><Document /></el-icon>
              <h4 style="margin-top:12px;">暂未解析</h4>
              <p style="color:var(--text-tertiary); font-size:13px; margin: 4px 0 16px;">点击下方按钮开始 AI 解析</p>
              <el-button type="primary" @click="analyzeJD" :loading="analyzing" style="width:100%;">
                {{ analyzing ? '解析中...' : '开始 AI 解析' }}
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { jdApi } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Document } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const jd = ref(null)
const parsed = ref(null)
const analyzing = ref(false)

const loadJD = async () => {
  try {
    const res = await jdApi.get(route.params.id)
    jd.value = res.data
    parsed.value = res.data?.parsed_result
  } catch (e) {
    ElMessage.error('加载JD失败')
    router.push('/jd')
  }
}

const analyzeJD = async () => {
  analyzing.value = true
  try {
    const res = await jdApi.analyze(route.params.id)
    parsed.value = res.data
    ElMessage.success('解析完成')
  } catch (e) {
    ElMessage.error('解析失败: ' + (e.message || ''))
  }
  finally { analyzing.value = false }
}

onMounted(loadJD)
</script>

<style scoped>
.jd-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.jd-info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.jd-info-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.jd-info-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.jd-content {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 13px;
  line-height: 1.7;
  max-height: 500px;
  overflow-y: auto;
  background: var(--bg-main);
  padding: 16px;
  border-radius: var(--radius-md);
  color: var(--text-primary);
}

/* 解析侧栏 */
.score-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
}

.score-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 10px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.skill-item {
  margin-bottom: 14px;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 13px;
  color: var(--text-primary);
}

.gap-tip {
  font-size: 12px;
  color: var(--warning);
  margin-top: 4px;
}

.soft-skills,
.keywords {
  display: flex;
  flex-wrap: wrap;
}

.unparsed-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 16px;
  text-align: center;
}
</style>
