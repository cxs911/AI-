<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Logo -->
      <div class="login-logo">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <h1>AI 求职助手</h1>
        <p class="login-subtitle">智能简历匹配 · 一站式投递管理</p>
      </div>

      <!-- 登录/注册切换 -->
      <div class="tab-bar">
        <span :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</span>
        <span :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</span>
      </div>

      <!-- 登录表单 -->
      <el-form v-if="mode === 'login'" ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" size="large" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" size="large" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 注册表单 -->
      <el-form v-else ref="registerFormRef" :model="registerForm" :rules="registerRules" class="login-form" @keyup.enter="handleRegister">
        <el-form-item prop="username">
          <el-input v-model="registerForm.username" placeholder="用户名" size="large" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item prop="display_name">
          <el-input v-model="registerForm.display_name" placeholder="显示名称（可选）" size="large" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="密码（至少6位）" size="large" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="confirm_password">
          <el-input v-model="registerForm.confirm_password" type="password" placeholder="确认密码" size="large" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="registering" @click="handleRegister">
            {{ registering ? '注册中...' : '注 册' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>首次使用请先注册账号</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store'
import { authApi } from '@/api/endpoints'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const mode = ref('login')
const loading = ref(false)
const registering = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

// 登录表单
const loginForm = reactive({ username: '', password: '' })
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 注册表单
const registerForm = reactive({
  username: '', display_name: '', password: '', confirm_password: '',
})
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少2位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== registerForm.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

const handleLogin = async () => {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await authApi.login({ username: loginForm.username, password: loginForm.password })
    if (res.code === 200) {
      authStore.login(res.data.token, res.data.user)
      ElMessage.success(`欢迎回来，${res.data.user.display_name}！`)
      router.push('/dashboard')
    }
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return
  registering.value = true
  try {
    const res = await authApi.register({
      username: registerForm.username,
      password: registerForm.password,
      display_name: registerForm.display_name || undefined,
    })
    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')
      // 自动填充用户名到登录表单
      loginForm.username = registerForm.username
      mode.value = 'login'
      registerForm.username = ''
      registerForm.display_name = ''
      registerForm.password = ''
      registerForm.confirm_password = ''
    }
  } catch { /* handled by interceptor */ }
  finally { registering.value = false }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0F172A 0%, #1B2A4A 50%, #1E3A5F 100%);
  padding: 20px;
}

.login-card {
  width: 420px;
  max-width: 100%;
  background: #FFFFFF;
  border-radius: 16px;
  padding: 40px 36px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-logo {
  text-align: center;
  margin-bottom: 24px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 12px;
}

.login-logo h1 {
  font-size: 24px;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 6px;
}

.login-subtitle {
  font-size: 14px;
  color: #94A3B8;
}

/* 标签切换 */
.tab-bar {
  display: flex;
  border-bottom: 1px solid #E2E8F0;
  margin-bottom: 24px;
}

.tab-bar span {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  color: #94A3B8;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tab-bar span.active {
  color: #3B82F6;
  border-bottom-color: #3B82F6;
}

.tab-bar span:hover {
  color: #3B82F6;
}

.login-form {
  margin-bottom: 20px;
}

.login-form .el-input__wrapper {
  padding: 4px 12px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
}

.login-footer {
  text-align: center;
  font-size: 12px;
  color: #94A3B8;
}
</style>
