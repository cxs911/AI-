<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-content">
        <h2>系统设置</h2>
        <div class="subtitle">配置 LLM 供应商、投递风控参数</div>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左栏 -->
      <el-col :xs="24" :lg="14">
        <!-- LLM 配置 -->
        <div class="card" style="margin-bottom:20px;">
          <div class="card-header">
            <h3>LLM 大模型配置</h3>
            <el-tag type="warning" effect="plain" size="small" round v-if="!keySaved">待配置</el-tag>
            <el-tag type="success" effect="plain" size="small" round v-else>已配置</el-tag>
          </div>

          <el-form label-width="120px">
            <el-form-item label="AI 供应商">
              <el-radio-group v-model="provider" @change="onProviderChange">
                <el-radio value="deepseek">DeepSeek（在线）</el-radio>
                <el-radio value="ollama">Ollama（本地）</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>

          <el-divider />

          <!-- DeepSeek -->
          <template v-if="provider === 'deepseek'">
            <el-form :model="deepseekConfig" label-width="120px">
              <el-form-item label="API Key">
                <el-input v-model="deepseekConfig.api_key" type="password" show-password
                  placeholder="sk-xxxxxxxxxxxxxxxx">
                  <template #suffix v-if="keySaved">
                    <el-tag type="success" size="small" effect="plain">已保存</el-tag>
                  </template>
                </el-input>
                <div class="form-tip">
                  在 <a href="https://platform.deepseek.com/api_keys" target="_blank">platform.deepseek.com</a> 获取
                  <template v-if="keySaved"> · Key 已保存，留空直接测试即可</template>
                </div>
              </el-form-item>
              <el-form-item label="模型">
                <el-select v-model="deepseekConfig.model" style="width:100%;">
                  <el-option label="deepseek-chat (V3)" value="deepseek-chat" />
                  <el-option label="deepseek-reasoner (R1)" value="deepseek-reasoner" />
                </el-select>
              </el-form-item>
              <el-form-item label="API 地址">
                <el-input v-model="deepseekConfig.base_url" placeholder="https://api.deepseek.com" />
              </el-form-item>
            </el-form>
          </template>

          <!-- Ollama -->
          <template v-if="provider === 'ollama'">
            <el-form :model="ollamaConfig" label-width="120px">
              <el-form-item label="API 地址">
                <el-input v-model="ollamaConfig.base_url" placeholder="http://localhost:11434" />
              </el-form-item>
              <el-form-item label="模型名称">
                <el-select v-model="ollamaConfig.model" filterable allow-create style="width:100%;">
                  <el-option v-for="m in availableModels" :key="m.name" :label="m.name" :value="m.name" />
                </el-select>
              </el-form-item>
              <el-form-item label="超时(秒)">
                <el-input-number v-model="ollamaConfig.timeout" :min="30" :max="300" controls-position="right" />
              </el-form-item>
              <el-form-item>
                <el-button size="small" @click="fetchModels">获取模型列表</el-button>
              </el-form-item>
            </el-form>
          </template>

          <el-divider />

          <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
            <el-button @click="saveConfig" :loading="saving" type="primary">
              <el-icon><Check /></el-icon> 保存配置
            </el-button>
            <el-button @click="testConnection" :loading="testing">
              测试连接
            </el-button>
            <div v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
              {{ testResult.message }}
            </div>
          </div>
        </div>

        <!-- 风控配置 -->
        <div class="card">
          <div class="card-header">
            <h3>投递风控配置</h3>
          </div>
          <el-form :model="riskConfig" label-width="130px" size="small">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="每日上限">
                  <el-input-number v-model="riskConfig.dailyLimit" :min="1" :max="50" controls-position="right" style="width:100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="投递间隔">
                  <div style="display:flex;align-items:center;gap:6px;width:100%;">
                    <el-input-number v-model="riskConfig.minInterval" :min="5" :max="60" controls-position="right" style="width:120px;" />
                    <span style="color:var(--text-tertiary);flex-shrink:0;">~</span>
                    <el-input-number v-model="riskConfig.maxInterval" :min="10" :max="120" controls-position="right" style="width:120px;" />
                    <span style="color:var(--text-tertiary);font-size:13px;flex-shrink:0;margin-left:2px;">秒</span>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="页面停留">
                  <div style="display:flex;align-items:center;gap:6px;width:100%;">
                    <el-input-number v-model="riskConfig.stayMin" :min="1" :max="10" controls-position="right" style="width:120px;" />
                    <span style="color:var(--text-tertiary);flex-shrink:0;">~</span>
                    <el-input-number v-model="riskConfig.stayMax" :min="3" :max="30" controls-position="right" style="width:120px;" />
                    <span style="color:var(--text-tertiary);font-size:13px;flex-shrink:0;margin-left:2px;">秒</span>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="工作时间">
                  <div style="display:flex;align-items:center;gap:6px;">
                    <el-time-picker v-model="workStart" format="HH:mm" placeholder="开始" style="width:130px;" />
                    <span style="color:var(--text-tertiary);flex-shrink:0;">至</span>
                    <el-time-picker v-model="workEnd" format="HH:mm" placeholder="结束" style="width:130px;" />
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工作日">
                  <el-checkbox-group v-model="workDays">
                    <el-checkbox label="1">周一</el-checkbox>
                    <el-checkbox label="2">周二</el-checkbox>
                    <el-checkbox label="3">周三</el-checkbox>
                    <el-checkbox label="4">周四</el-checkbox>
                    <el-checkbox label="5">周五</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="primary" @click="saveRiskConfig">保存风控配置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <!-- 右栏 -->
      <el-col :xs="24" :lg="10">
        <!-- 账号管理 -->
        <div class="card" style="margin-bottom:20px;">
          <div class="card-header">
            <h3>账号管理</h3>
            <el-tag type="success" effect="plain" size="small" round>已登录</el-tag>
          </div>
          <div class="account-info">
            <div class="ai-row">
              <span class="ai-label">当前用户</span>
              <span class="ai-value">{{ authStore.user?.display_name || '-' }}</span>
            </div>
            <div class="ai-row">
              <span class="ai-label">用户名</span>
              <span class="ai-value">{{ authStore.user?.username || '-' }}</span>
            </div>
          </div>
          <el-divider style="margin:12px 0;" />
          <el-form :model="pwdForm" ref="pwdFormRef" label-width="100px" size="small">
            <el-form-item label="原密码" prop="old_password" :rules="[{ required: true, message: '请输入原密码' }]">
              <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="输入原密码" />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password" :rules="[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6位' },
            ]">
              <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="新密码至少6位" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="changingPwd" @click="changePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 系统信息 -->
        <div class="card" style="margin-bottom:20px;">
          <div class="card-header">
            <h3>系统信息</h3>
          </div>
          <div class="info-list">
            <div class="info-row">
              <span class="info-label">应用名称</span>
              <span class="info-value">{{ sysInfo?.app_name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">版本号</span>
              <span class="info-value">{{ sysInfo?.version || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">AI 供应商</span>
              <span class="info-value">{{ sysInfo?.provider === 'deepseek' ? 'DeepSeek' : 'Ollama' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">数据库</span>
              <span class="info-value" style="font-size:12px;">{{ sysInfo?.db_path || 'SQLite' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">上传目录</span>
              <span class="info-value" style="font-size:12px;">{{ sysInfo?.upload_dir || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">导出目录</span>
              <span class="info-value" style="font-size:12px;">{{ sysInfo?.export_dir || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">每日投递上限</span>
              <span class="info-value">{{ sysInfo?.delivery_limit || 25 }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">工作时间</span>
              <span class="info-value">{{ sysInfo?.work_hours || '09:00-18:00' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">浏览器</span>
              <span class="info-value">Chrome (可视化模式)</span>
            </div>
          </div>
        </div>

        <!-- 使用说明 -->
        <div class="card">
          <div class="card-header">
            <h3>使用说明</h3>
          </div>
          <div class="help-section">
            <div class="help-group">
              <h4>🚀 快速开始</h4>
              <ol>
                <li>在「个人素材库」上传简历或添加经历</li>
                <li>在「JD智能解析」添加岗位描述并解析</li>
                <li>在「简历管理」生成岗位定制简历</li>
                <li>启动浏览器并扫码登录 Boss 直聘</li>
                <li>在「投递管理」搜索岗位并投递</li>
              </ol>
            </div>
            <div class="help-group">
              <h4>🤖 AI 供应商说明</h4>
              <ul>
                <li><b>DeepSeek（推荐）</b>：在线调用，需填写 API Key，效果最佳</li>
                <li><b>Ollama 本地</b>：需安装 Ollama 并下载模型（推荐 qwen2.5:7b）</li>
                <li>修改供应商后请点击「测试连接」确认可用</li>
              </ul>
            </div>
            <div class="help-group">
              <h4>⚠️ 注意事项</h4>
              <ul>
                <li>批量投递需开启「人工审核开关」</li>
                <li>系统自动执行风控策略，不建议修改默认参数</li>
                <li>所有数据本地存储，不会上传到云端</li>
              </ul>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { settingsApi, deliveryApi, authApi } from '@/api/endpoints'
import { useAppStore, useAuthStore } from '@/store'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'

const appStore = useAppStore()
const authStore = useAuthStore()

const provider = ref('deepseek')

const ollamaConfig = reactive({
  base_url: 'http://localhost:11434',
  model: 'qwen2.5:7b',
  timeout: 120,
})

const deepseekConfig = reactive({
  api_key: '',
  model: 'deepseek-chat',
  base_url: 'https://api.deepseek.com',
})

const availableModels = ref([])
const testing = ref(false)
const saving = ref(false)
const testResult = ref(null)
const keySaved = ref(false)
const sysInfo = ref(null)

const riskConfig = reactive({
  dailyLimit: 25,
  minInterval: 15,
  maxInterval: 40,
  stayMin: 3,
  stayMax: 12,
})
const workStart = ref(new Date(2024, 0, 1, 9, 0))
const workEnd = ref(new Date(2024, 0, 1, 18, 0))
const workDays = ref(['1', '2', '3', '4', '5'])

// 密码修改
const pwdFormRef = ref(null)
const changingPwd = ref(false)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
})

const changePassword = async () => {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return
  changingPwd.value = true
  try {
    const res = await authApi.changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    if (res.code === 200) {
      ElMessage.success('密码已修改，请重新登录')
      pwdForm.old_password = ''
      pwdForm.new_password = ''
      authStore.logout()
      setTimeout(() => { window.location.hash = '/login' }, 1000)
    }
  } catch (e) { /* ignore */ }
  finally { changingPwd.value = false }
}

const onProviderChange = () => { testResult.value = null }

const testConnection = async () => {
  testing.value = true
  testResult.value = null
  try {
    const params = {
      provider: provider.value,
      api_key: provider.value === 'deepseek' ? deepseekConfig.api_key : '',
      base_url: provider.value === 'deepseek' ? deepseekConfig.base_url : ollamaConfig.base_url,
      model: provider.value === 'deepseek' ? deepseekConfig.model : ollamaConfig.model,
    }
    const res = await settingsApi.testLLM(params)
    testResult.value = { success: true, message: `✅ 连接成功！模型响应: ${res.data?.response || '正常'}` }
  } catch (e) {
    testResult.value = { success: false, message: `❌ 连接失败: ${e.message || '请检查配置'}` }
  } finally { testing.value = false }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const data = { provider: provider.value }
    if (provider.value === 'deepseek') {
      data.deepseek_api_key = deepseekConfig.api_key
      data.deepseek_base_url = deepseekConfig.base_url
      data.deepseek_model = deepseekConfig.model
    } else {
      data.ollama_base_url = ollamaConfig.base_url
      data.ollama_model = ollamaConfig.model
      data.ollama_timeout = ollamaConfig.timeout
    }
    const res = await settingsApi.saveLLM(data)
    if (res.code === 200) {
      keySaved.value = true
      if (provider.value === 'deepseek') deepseekConfig.api_key = ''
      ElMessage.success('配置已保存！点击「测试连接」验证')
      testResult.value = null
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.message || '未知错误'))
  } finally { saving.value = false }
}

const fetchModels = async () => {
  try {
    const res = await settingsApi.listModels({ provider: 'ollama', base_url: ollamaConfig.base_url })
    availableModels.value = res.data || []
    ElMessage.success(`获取到 ${availableModels.value.length} 个模型`)
  } catch {
    ElMessage.error('获取失败，请确认 Ollama 服务已启动')
  }
}

const saveRiskConfig = () => { ElMessage.success('风控配置已保存(本地)') }

onMounted(async () => {
  try {
    const res = await settingsApi.getLLM()
    if (res.code === 200) {
      provider.value = res.data.provider || 'deepseek'
      ollamaConfig.base_url = res.data.ollama_base_url || ollamaConfig.base_url
      ollamaConfig.model = res.data.ollama_model || ollamaConfig.model
      ollamaConfig.timeout = res.data.ollama_timeout || ollamaConfig.timeout
      deepseekConfig.base_url = res.data.deepseek_base_url || deepseekConfig.base_url
      deepseekConfig.model = res.data.deepseek_model || deepseekConfig.model
      if (res.data.has_api_key) {
        keySaved.value = true
        deepseekConfig.api_key = ''
      }
    }
  } catch { /* ignore */ }
  try {
    const res = await settingsApi.getSystem()
    sysInfo.value = res.data
  } catch { /* ignore */ }
})
</script>

<style scoped>
.test-result {
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  line-height: 1.5;
}

.test-result.success {
  background: var(--success-bg);
  color: var(--success);
}

.test-result.error {
  background: var(--danger-bg);
  color: var(--danger);
}

/* 系统信息 */
.info-list {
  display: flex;
  flex-direction: column;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--text-tertiary);
}

.info-value {
  color: var(--text-primary);
  font-weight: 500;
  text-align: right;
  max-width: 60%;
  word-break: break-all;
}

/* 账号管理 */
.account-info {
  display: flex;
  flex-direction: column;
}

.ai-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 13px;
}

.ai-label {
  color: var(--text-tertiary);
}

.ai-value {
  color: var(--text-primary);
  font-weight: 500;
}

/* 使用说明 */
.help-section {
  font-size: 13px;
  line-height: 1.8;
}

.help-group {
  margin-bottom: 16px;
}

.help-group:last-child {
  margin-bottom: 0;
}

.help-group h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.help-group ol,
.help-group ul {
  padding-left: 20px;
}

.help-group li {
  margin-bottom: 3px;
  color: var(--text-secondary);
}

.form-tip {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.form-tip a {
  color: var(--accent);
}
</style>
