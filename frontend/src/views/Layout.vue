<template>
  <el-container class="layout-container">
    <!-- ===== 侧边栏 ===== -->
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '240px'" class="sidebar">
      <!-- Logo区 -->
      <div class="logo" @click="router.push('/dashboard')">
        <div class="logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <transition name="el-fade-in-linear">
          <span v-show="!appStore.sidebarCollapsed" class="logo-text">AI 求职助手</span>
        </transition>
      </div>

      <!-- 导航菜单 -->
      <el-menu
        :default-active="route.path"
        :collapse="appStore.sidebarCollapsed"
        router
        :collapse-transition="false"
        background-color="transparent"
        text-color="#94A3B8"
        active-text-color="#FFFFFF"
      >
        <!-- 工作台 -->
        <el-menu-item index="/dashboard">
          <el-icon size="18"><DataAnalysis /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <!-- 求职中心（分组） -->
        <el-sub-menu index="job-center">
          <template #title>
            <el-icon size="18"><FolderOpened /></el-icon>
            <span>求职中心</span>
          </template>
          <el-menu-item index="/materials">
            <el-icon size="16"><Folder /></el-icon>
            <template #title>个人素材库</template>
          </el-menu-item>
          <el-menu-item index="/jd">
            <el-icon size="16"><Document /></el-icon>
            <template #title>JD智能解析</template>
          </el-menu-item>
          <el-menu-item index="/resumes">
            <el-icon size="16"><Notebook /></el-icon>
            <template #title>简历管理</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 投递管理 -->
        <el-menu-item index="/delivery">
          <el-icon size="18"><Promotion /></el-icon>
          <template #title>投递管理</template>
        </el-menu-item>

        <!-- 底部分隔线 + 设置入口 -->
        <div class="menu-bottom-spacer"></div>

        <el-menu-item index="/settings">
          <el-icon size="18"><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>

      <!-- 底部 LLM 状态 -->
      <div class="sidebar-footer" v-show="!appStore.sidebarCollapsed">
        <div class="sidebar-footer-inner" @click="router.push('/settings')">
          <span class="footer-dot" :class="llmOnline ? 'online' : 'offline'"></span>
          <div class="footer-info">
            <span class="footer-label">{{ llmProvider === 'deepseek' ? 'DeepSeek' : 'Ollama' }}</span>
            <span class="footer-status">{{ llmOnline ? '已连接' : '未连接' }}</span>
          </div>
        </div>
      </div>
    </el-aside>

    <!-- ===== 主区域 ===== -->
    <el-container>
      <!-- 顶栏 -->
      <el-header class="topbar">
        <div class="topbar-left">
          <el-icon class="collapse-btn" @click="appStore.toggleSidebar" :size="18">
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <div class="current-page-title">
            {{ route.meta.title || '工作台' }}
          </div>
        </div>
        <div class="topbar-right">
          <!-- LLM 状态徽章 -->
          <div class="llm-badge" :class="{ connected: llmOnline }" @click="router.push('/settings')">
            <span class="llm-dot"></span>
            <span>{{ llmOnline ? 'LLM 已连接' : 'LLM 离线' }}</span>
          </div>

          <!-- 用户 -->
          <el-dropdown trigger="click">
            <span class="user-avatar">
              <el-avatar :size="30" icon="UserFilled" />
              <span class="user-name">{{ authStore.user?.display_name || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/settings')">
                  <el-icon size="14"><Setting /></el-icon>系统设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="openAbout">
                  <el-icon size="14"><InfoFilled /></el-icon>关于
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon size="14" color="#EF4444"><SwitchButton /></el-icon>
                  <span style="color:#EF4444;">退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore, useAuthStore } from '@/store'
import { settingsApi, authApi } from '@/api/endpoints'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  Fold, Expand, DataAnalysis, FolderOpened, Folder, Document,
  Notebook, Promotion, Setting, InfoFilled, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()
const llmOnline = ref(false)
const llmProvider = ref('deepseek')

const checkLLM = async () => {
  try {
    const cfg = await settingsApi.getLLM()
    if (cfg.code === 200) {
      llmProvider.value = cfg.data.provider || 'ollama'
      const p = cfg.data.provider
      const baseUrl = p === 'deepseek' ? cfg.data.deepseek_base_url : cfg.data.ollama_base_url
      const model = p === 'deepseek' ? cfg.data.deepseek_model : cfg.data.ollama_model
      const res = await settingsApi.testLLM({
        provider: p, base_url: baseUrl, model, api_key: ''
      })
      llmOnline.value = res.code === 200
    }
  } catch {
    llmOnline.value = false
  }
}

const openAbout = () => {
  ElMessageBox.alert(
    '<b>AI 求职助手</b> v2.0<br><br>' +
    '基于 Vue3 + FastAPI + SQLite 构建<br>' +
    '支持 DeepSeek / Ollama 大模型',
    '关于',
    { dangerouslyUseHTMLString: true, confirmButtonText: '知道了' }
  )
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch { /* ignore */ }
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(checkLLM)
</script>

<style scoped>
/* ===== 整体容器 ===== */
.layout-container {
  height: 100vh;
}

/* ===== 侧边栏 ===== */
.sidebar {
  background: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.25s ease;
  border-right: none;
  z-index: 10;
}

/* Logo */
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 18px;
  color: #FFFFFF;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--accent), #8B5CF6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.logo-text {
  font-size: 15px;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.3px;
}

/* 导航菜单 */
.el-menu {
  border-right: none !important;
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

/* 一级菜单项 */
.el-menu-item {
  height: 42px;
  line-height: 42px;
  margin: 2px 8px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.15s ease;
}

.el-menu-item:hover {
  background: var(--bg-sidebar-hover) !important;
  color: #E2E8F0 !important;
}

.el-menu-item.is-active {
  background: var(--bg-sidebar-active) !important;
  color: #FFFFFF !important;
  font-weight: 500;
}

/* 子菜单标题 */
:deep(.el-sub-menu__title) {
  height: 42px;
  line-height: 42px;
  margin: 2px 8px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.15s ease;
  padding-right: 8px;
}

:deep(.el-sub-menu__title:hover) {
  background: var(--bg-sidebar-hover) !important;
  color: #E2E8F0 !important;
}

/* 子菜单项 */
:deep(.el-menu--inline) .el-menu-item {
  padding-left: 50px !important;
  height: 38px;
  line-height: 38px;
  margin: 1px 8px;
  font-size: 13px;
  border-radius: 6px;
}

:deep(.el-menu--inline) .el-menu-item:hover {
  background: var(--bg-sidebar-hover) !important;
}

:deep(.el-menu--inline) .el-menu-item.is-active {
  background: var(--bg-sidebar-active) !important;
  color: #FFFFFF !important;
}

/* 子菜单展开箭头 */
:deep(.el-sub-menu__title .el-sub-menu__icon-arrow) {
  font-size: 12px;
  color: #64748B;
}

/* 底部分隔 */
.menu-bottom-spacer {
  flex: 1;
  min-height: 8px;
}

/* 底部状态栏 */
.sidebar-footer {
  flex-shrink: 0;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 12px 16px;
}

.sidebar-footer-inner {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 8px;
  transition: background 0.15s;
}

.sidebar-footer-inner:hover {
  background: var(--bg-sidebar-hover);
}

.footer-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  position: relative;
}

.footer-dot.online {
  background: var(--success);
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}

.footer-dot.offline {
  background: var(--text-tertiary);
}

.footer-info {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.footer-label {
  font-size: 13px;
  font-weight: 500;
  color: #E2E8F0;
}

.footer-status {
  font-size: 11px;
  color: var(--text-tertiary);
}

/* ===== 顶栏 ===== */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #FFFFFF;
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
  height: 56px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.collapse-btn {
  cursor: pointer;
  color: var(--text-tertiary);
  transition: color 0.15s;
}

.collapse-btn:hover {
  color: var(--text-primary);
}

.current-page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* LLM 状态徽章 */
.llm-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-tertiary);
  background: var(--bg-main);
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid var(--border-light);
}

.llm-badge:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.llm-badge.connected {
  color: var(--success);
  border-color: var(--success-bg);
  background: var(--success-bg);
}

.llm-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

/* 用户头像 */
.user-avatar {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.user-avatar .el-avatar {
  border: 2px solid var(--border-light);
  transition: border-color 0.15s;
}

.user-avatar:hover .el-avatar {
  border-color: var(--accent);
}

/* ===== 内容区 ===== */
.main-content {
  background: var(--bg-main);
  min-height: calc(100vh - 56px);
  padding: 0;
  overflow-y: auto;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .sidebar {
    width: 64px !important;
  }
  .topbar {
    padding: 0 12px;
  }
  .current-page-title {
    font-size: 14px;
  }
}
</style>
