<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { Promotion, UserFilled, Service, SwitchButton } from '@element-plus/icons-vue'
import { useChat } from './composables/useChat'
import MarkdownIt from 'markdown-it'
import Login from './composables/Login.vue'

const md = new MarkdownIt({ html: true, linkify: true, typographer: true })

const { messages, loading, sendMessage, clearChat } = useChat()
const inputQuery = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const isLoggedIn = ref(false) // 登录状态

// 检查是否已登录
onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    isLoggedIn.value = true
  }
})

const handleLoginSuccess = () => {
  isLoggedIn.value = true
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  isLoggedIn.value = false
  clearChat() // 清空历史
}

const handleSend = async () => {
  if (!inputQuery.value.trim() || loading.value) return
  const query = inputQuery.value
  inputQuery.value = ''
  await sendMessage(query)
}

watch(messages, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTo({ top: chatContainer.value.scrollHeight, behavior: 'smooth' })
  }
}, { deep: true })
</script>

<template>
  <div class="app-background">

    <transition name="fade" mode="out-in">
      <Login v-if="!isLoggedIn" @login-success="handleLoginSuccess" />

      <div v-else class="main-card">
        <header class="chat-header">
          <div class="header-content">
            <div class="logo-box">
              <el-icon :size="24" color="#409EFF"><Service /></el-icon>
            </div>
            <div class="header-text">
              <h2>AI 开发助手</h2>
              <div class="status-dot">
                <span class="dot"></span>
                <span class="status-text">已连接 | 用户中心</span>
              </div>
            </div>
          </div>
          <el-button circle :icon="SwitchButton" type="danger" plain size="small" @click="handleLogout" title="退出登录" />
        </header>

        <div class="chat-box" ref="chatContainer">
          <div v-if="messages.length === 0" class="welcome-screen">
            <el-icon :size="60" color="#E5EAF3"><Service /></el-icon>
            <p>有什么关于大模型开发的问题吗？</p>
          </div>

          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message-row"
            :class="[msg.role, { 'typing': loading && index === messages.length - 1 && msg.role === 'assistant' }]"
          >
            <div class="avatar shadow-sm">
              <el-icon v-if="msg.role === 'user'" :size="20"><UserFilled /></el-icon>
              <el-icon v-else :size="20"><Service /></el-icon>
            </div>
            <div class="message-content">
              <div class="bubble shadow-sm">
                <div v-if="msg.role === 'assistant'" class="markdown-body" v-html="md.render(msg.content)"></div>
                <div v-else>{{ msg.content }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="input-wrapper shadow-md">
            <el-input
              v-model="inputQuery"
              placeholder="输入你的问题..."
              @keyup.enter="handleSend"
              :disabled="loading"
              class="custom-input"
              resize="none"
            >
              <template #suffix>
                <el-button type="primary" circle :icon="Promotion" @click="handleSend" :disabled="!inputQuery.trim() || loading" class="send-btn" />
              </template>
            </el-input>
          </div>
          <p class="footer-tip">Powered by LangChain & Alibaba Qwen</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* 这里保留之前的样式，并补充过渡动画 */
.app-background {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 简单的淡入淡出动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* ... 以下请保留之前 App.vue 中的 main-card, chat-header, chat-box 等所有样式 ... */
/* 为了节省篇幅，请确保你把之前 App.vue 里的 <style> 内容完整复制过来 */
/* 如果你之前覆盖了，这里需要把你刚才“美化后”的 CSS 再粘贴一遍 */

.main-card {
  width: 100%;
  max-width: 900px;
  height: 95vh;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.chat-header {
  height: 70px;
  padding: 0 24px;
  display: flex;
  justify-content: space-between; /* 修改这里让退出按钮靠右 */
  align-items: center;
  border-bottom: 1px solid rgba(0,0,0,0.06);
  background: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}

.header-content { display: flex; align-items: center; gap: 16px; }
.logo-box { width: 40px; height: 40px; background: #ecf5ff; border-radius: 12px; display: flex; justify-content: center; align-items: center; }
.header-text h2 { margin: 0; font-size: 18px; color: #2c3e50; font-weight: 600; }
.status-dot { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #67c23a; margin-top: 2px; }
.dot { width: 8px; height: 8px; background-color: #67c23a; border-radius: 50%; box-shadow: 0 0 4px #67c23a; }

.chat-box { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; scroll-behavior: smooth; }
.chat-box::-webkit-scrollbar { width: 6px; }
.chat-box::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 3px; }
.welcome-screen { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #909399; gap: 16px; }

.message-row { display: flex; gap: 16px; max-width: 85%; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.message-row.user { flex-direction: row-reverse; align-self: flex-end; }
.avatar { width: 40px; height: 40px; border-radius: 12px; display: flex; justify-content: center; align-items: center; flex-shrink: 0; font-weight: bold; }
.message-row.user .avatar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.message-row.assistant .avatar { background: #ffffff; color: #409EFF; border: 1px solid #eef0f5; }
.message-content { display: flex; flex-direction: column; gap: 4px; max-width: 100%; }
.bubble { padding: 14px 18px; border-radius: 18px; font-size: 15px; line-height: 1.6; position: relative; word-wrap: break-word; }
.message-row.user .bubble { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-bottom-right-radius: 4px; }
.message-row.assistant .bubble { background: white; color: #2c3e50; border-bottom-left-radius: 4px; }
.shadow-sm { box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

.input-area { padding: 24px; background: rgba(255,255,255,0.6); border-top: 1px solid rgba(0,0,0,0.05); display: flex; flex-direction: column; align-items: center; gap: 8px; }
.input-wrapper { width: 100%; border-radius: 24px; background: white; padding: 4px 6px 4px 16px; border: 1px solid #e4e7ed; transition: all 0.3s; display: flex; align-items: center; }
.input-wrapper:focus-within { border-color: #409EFF; box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1); }
.shadow-md { box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
:deep(.el-input__wrapper) { box-shadow: none !important; padding: 0; background: transparent; }
:deep(.el-input__inner) { border: none; height: 44px; font-size: 15px; color: #333; }
.send-btn { border-radius: 50% !important; width: 40px; height: 40px; transition: transform 0.2s; }
.send-btn:hover { transform: scale(1.05); }
.footer-tip { font-size: 12px; color: #b1b3b8; margin: 0; }

:deep(.markdown-body p) { margin-bottom: 12px; }
:deep(.markdown-body p:last-child) { margin-bottom: 0; }
:deep(.markdown-body pre) { background: #f6f8fa; padding: 12px; border-radius: 8px; overflow-x: auto; border: 1px solid #e1e4e8; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 13px; }
:deep(.markdown-body code) { background: rgba(175, 184, 193, 0.2); padding: 2px 4px; border-radius: 4px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.9em; }
</style>