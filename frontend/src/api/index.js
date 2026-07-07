/** API客户端 - 统一请求封装 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '@/store'

const request = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截 — 自动注入 Token
request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message))
    }
    return res
  },
  (error) => {
    // 401 未登录，跳转登录页
    if (error.response?.status === 401) {
      removeToken()
      window.location.hash = '/login'
      ElMessage.warning('登录已过期，请重新登录')
      return Promise.reject(error)
    }
    const msg = error.response?.data?.detail || error.message || '网络错误'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default request
