<script setup lang="ts">
import { ref, reactive } from 'vue'
import { User, Lock, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['login-success'])

const isRegister = ref(false) // 切换登录/注册
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true

  // 根据状态决定是登录还是注册
  const endpoint = isRegister.value ? '/api/auth/register' : '/api/auth/token'

  try {
    const res = await fetch(`http://localhost:8000${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(data.detail || '请求失败')
    }

    if (isRegister.value) {
      ElMessage.success('注册成功！请登录')
      isRegister.value = false // 切换回登录页
    } else {
      // 登录成功
      ElMessage.success('登录成功')
      // 1. 保存 Token
      localStorage.setItem('access_token', data.access_token)
      // 2. 通知父组件
      emit('login-success')
    }
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-card shadow-lg">
    <div class="login-header">
      <h2>{{ isRegister ? '创建账号' : '欢迎回来' }}</h2>
      <p>LLM Dev Assistant 智能客服</p>
    </div>

    <div class="form-area">
      <el-input
        v-model="form.username"
        placeholder="用户名"
        :prefix-icon="User"
        size="large"
        class="mb-4"
      />
      <el-input
        v-model="form.password"
        placeholder="密码"
        type="password"
        :prefix-icon="Lock"
        size="large"
        show-password
        @keyup.enter="handleSubmit"
      />

      <el-button
        type="primary"
        size="large"
        class="submit-btn"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ isRegister ? '立即注册' : '登录' }}
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </div>

    <div class="footer">
      <span>{{ isRegister ? '已有账号？' : '还没有账号？' }}</span>
      <a href="#" @click.prevent="isRegister = !isRegister">
        {{ isRegister ? '去登录' : '去注册' }}
      </a>
    </div>
  </div>
</template>

<style scoped>
.login-card {
  width: 400px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.login-header h2 { margin-bottom: 8px; color: #333; }
.login-header p { color: #888; margin-bottom: 30px; font-size: 14px; }

.form-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.submit-btn {
  width: 100%;
  border-radius: 12px;
  font-weight: bold;
  margin-top: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.submit-btn:hover {
  opacity: 0.9;
}

.footer {
  margin-top: 24px;
  font-size: 14px;
  color: #666;
}

.footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
  margin-left: 5px;
}

.shadow-lg { box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
</style>