// src/utils/request.js
import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',        // 基础URL，所有请求都会自动加上 /api
  timeout: 10000,         // 请求超时时间（10秒）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 🛡️ 请求拦截器 - 在发送请求前执行
request.interceptors.request.use((config) => {
  // 自动添加认证 token
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  console.log('🚀 发送请求:', config.method?.toUpperCase(), config.url)
  return config
})

// 🛡️ 响应拦截器 - 在收到响应后执行
request.interceptors.response.use(
  (response) => {
    // 成功响应处理
    console.log('✅ 请求成功:', response.config.url)
    return response.data  // 直接返回数据部分
  },
  (error) => {
    // 错误响应处理
    console.error('❌ 请求失败:', error.response?.status, error.config?.url)
    
    if (error.response?.status === 401) {
      // Token 过期，跳转到登录页
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default request