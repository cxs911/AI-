/** 全局状态管理 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { settingsApi } from '@/api/endpoints'

// ===== Token 管理 =====
const TOKEN_KEY = 'ai_job_token'
const USER_KEY = 'ai_job_user'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getSavedUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

// ===== 应用 Store =====
export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const toggleSidebar = () => { sidebarCollapsed.value = !sidebarCollapsed.value }

  const systemInfo = ref(null)
  const ollamaConfig = ref({ base_url: 'http://localhost:11434', model: 'qwen2.5:7b' })

  const loadSystemInfo = async () => {
    try {
      const res = await settingsApi.getSystem()
      if (res.code === 200) systemInfo.value = res.data
    } catch (e) { /* ignore */ }
  }

  const loadOllamaConfig = async () => {
    try {
      const res = await settingsApi.getLLM()
      if (res.code === 200) {
        ollamaConfig.value = {
          base_url: res.data.ollama_base_url || res.data.base_url || 'http://localhost:11434',
          model: res.data.ollama_model || res.data.model || 'qwen2.5:7b',
          timeout: res.data.ollama_timeout || res.data.timeout || 120,
          provider: res.data.provider || 'deepseek',
        }
      }
    } catch (e) { /* ignore */ }
  }

  return {
    sidebarCollapsed, toggleSidebar,
    systemInfo, ollamaConfig,
    loadSystemInfo, loadOllamaConfig,
  }
})

// ===== 用户认证 Store =====
export const useAuthStore = defineStore('auth', () => {
  const user = ref(getSavedUser())
  const token = ref(getToken())

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  function login(tokenStr, userData) {
    token.value = tokenStr
    user.value = userData
    setToken(tokenStr)
    saveUser(userData)
  }

  function logout() {
    token.value = null
    user.value = null
    removeToken()
  }

  return { user, token, isLoggedIn, login, logout }
})

// ===== 投递管理 Store =====
export const useDeliveryStore = defineStore('delivery', () => {
  const browserRunning = ref(false)
  const isPaused = ref(false)
  const todayDeliveries = ref(0)
  const manualReviewEnabled = ref(false)

  return {
    browserRunning, isPaused, todayDeliveries, manualReviewEnabled,
  }
})
