/** API端点汇总 */
import request from './index'

// ===== 素材库 =====
export const materialApi = {
  upload: (formData) => request.post('/materials/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  list: (params) => request.get('/materials/list', { params }),
  get: (id) => request.get(`/materials/${id}`),
  delete: (id) => request.delete(`/materials/${id}`),
  // 标签
  createTag: (data) => request.post('/materials/tags', data),
  listTags: () => request.get('/materials/tags'),
  // 经历
  createExperience: (data) => request.post('/materials/experiences', data),
  listExperiences: (params) => request.get('/materials/experiences', { params }),
  optimizeExperience: (id, data) => request.post(`/materials/experiences/${id}/optimize`, data),
  deleteExperience: (id) => request.delete(`/materials/experiences/${id}`),
}

// ===== JD管理 =====
export const jdApi = {
  create: (data) => request.post('/jd', data),
  analyze: (id) => request.post(`/jd/${id}/analyze`),
  list: (params) => request.get('/jd/list', { params }),
  get: (id) => request.get(`/jd/${id}`),
  delete: (id) => request.delete(`/jd/${id}`),
  getKeywords: (id) => request.get(`/jd/${id}/keywords`),
}

// ===== 简历 =====
export const resumeApi = {
  generate: (data) => request.post('/resumes/generate', data),
  greeting: (id, data) => request.post(`/resumes/${id}/greeting`, data),
  list: (params) => request.get('/resumes/list', { params }),
  get: (id) => request.get(`/resumes/${id}`),
  delete: (id) => request.delete(`/resumes/${id}`),
  exportPdf: (id) => request.post(`/resumes/${id}/export/pdf`),
  preview: (id) => request.get(`/resumes/${id}/preview`),
}

// ===== 投递管理 =====
export const deliveryApi = {
  // 浏览器
  startBrowser: () => request.post('/delivery/browser/start'),
  waitLogin: (params) => request.post('/delivery/browser/wait-login', null, { params }),
  closeBrowser: () => request.post('/delivery/browser/close'),
  browserStatus: () => request.get('/delivery/browser/status'),
  // 搜索
  searchJobs: (data) => request.post('/delivery/search', data),
  // 投递列表
  listJobs: (params) => request.get('/delivery/jobs', { params }),
  deliverSingle: (jobId) => request.post(`/delivery/jobs/${jobId}/deliver`),
  deliverBatch: (data) => request.post('/delivery/batch-deliver', data),
  // 统计
  getStats: (params) => request.get('/delivery/stats', { params }),
  // 风控
  getRiskConfig: () => request.get('/delivery/risk-config'),
  updateRiskConfig: (data) => request.post('/delivery/risk-config', data),
}

// ===== 设置 =====
export const settingsApi = {
  getLLM: () => request.get('/settings/llm'),
  testLLM: (data) => request.post('/settings/llm/test', data),
  saveLLM: (data) => request.post('/settings/llm/save', data),
  listModels: (params) => request.get('/settings/llm/models', { params }),
  getSystem: () => request.get('/settings/system'),
}

// ===== 用户认证 =====
export const authApi = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data),
  logout: () => request.post('/auth/logout'),
  getMe: () => request.get('/auth/me'),
  changePassword: (data) => request.post('/auth/change-password', data),
}
