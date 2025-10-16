// src/utils/auth.js

export const auth = {
  // 💾 保存 token 到本地存储
  setToken(token) {
    localStorage.setItem('auth_token', token)
    console.log('🔐 Token 已保存')
  },
  
  // 📥 获取 token
  getToken() {
    return localStorage.getItem('auth_token')
  },
  
  // 🗑️ 删除 token（退出登录）
  removeToken() {
    localStorage.removeItem('auth_token')
    console.log('🔓 Token 已删除')
  },
  
  // 🔍 检查用户是否已登录
  isAuthenticated() {
    return !!this.getToken()
  },
  
  // 🔄 解析 JWT token 获取用户信息
  parseToken(token) {
    try {
      const payload = token.split('.')[1]  // JWT 第二部分是 payload
      const decoded = JSON.parse(atob(payload))
      console.log('👤 用户信息:', decoded)
      return decoded
    } catch (error) {
      console.error('❌ Token 解析失败:', error)
      return null
    }
  },
  
  // ⏰ 检查 token 是否即将过期
  isTokenExpiringSoon(token, thresholdMinutes = 5) {
    const payload = this.parseToken(token)
    if (!payload || !payload.exp) return false
    
    const now = Math.floor(Date.now() / 1000)
    const expiresIn = payload.exp - now
    return expiresIn < (thresholdMinutes * 60)
  }
}