<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  // 表单验证
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码';
    return;
  }
  
  error.value = '';
  loading.value = true;
  
  try {
    // 模拟登录请求
    // 实际项目中应替换为真实的后端API
    // const response = await axios.post('/api/auth/login', {
    //   username: username.value,
    //   password: password.value
    // });
    
    // 模拟成功登录
    setTimeout(() => {
      // 保存token到localStorage
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('user', JSON.stringify({ username: username.value }));
      
      router.push('/dashboard');
      loading.value = false;
    }, 1000);
  } catch (err) {
    error.value = '登录失败，请检查用户名和密码';
    loading.value = false;
  }
};
</script>

<template>
  <v-app class="login-container">
    <v-card class="login-card" elevation="8">
      <v-card-title class="text-center mb-4 pb-2">
        <h1 class="text-h4 font-bold">智慧社区管理平台</h1>
      </v-card-title>
      
      <v-card-text>
        <v-form @submit.prevent="handleLogin">
          <div v-if="error" class="mb-4">
            <v-alert
              type="error"
              :value="true"
              dense
              class="text-center"
            >
              {{ error }}
            </v-alert>
          </div>
          
          <v-text-field
            v-model="username"
            label="用户名"
            prepend-icon="mdi-account"
            required
            solo
            class="mb-4"
            :disabled="loading"
          ></v-text-field>
          
          <v-text-field
            v-model="password"
            label="密码"
            prepend-icon="mdi-lock"
            type="password"
            required
            solo
            class="mb-6"
            :disabled="loading"
          ></v-text-field>
          
          <v-btn
            type="submit"
            color="primary"
            block
            :loading="loading"
            :disabled="loading"
            class="login-button"
          >
            登录
          </v-btn>
        </v-form>
      </v-card-text>
      
      <v-card-actions class="justify-center pt-0 pb-4">
        <v-btn
          text
          small
          class="text-primary"
          :disabled="loading"
        >
          忘记密码？
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-app>
</template>

<style scoped>
/* 确保登录容器完全居中 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
}

/* 登录卡片样式 */
.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin: auto; /* 添加自动外边距确保居中 */
}

.login-button {
  font-size: 16px;
  padding: 10px 0;
  text-transform: none;
}

/* 添加一个全局样式块来重置body和html样式 */
:global(html), :global(body) {
  margin: 0;
  padding: 0;
  height: 100%;
}

:global(#app) {
  height: 100%;
}
</style>