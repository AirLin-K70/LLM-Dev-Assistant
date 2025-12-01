import { ref } from 'vue'
import { ElMessage } from 'element-plus'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export function useChat() {
  const messages = ref<Message[]>([
    { role: 'assistant', content: '你好！我是你的大模型开发助手，有什么可以帮你的吗？' }
  ])
  const loading = ref(false)

  const sendMessage = async (query: string) => {
    if (!query.trim()) return

    // 1. 获取 Token
    const token = localStorage.getItem('access_token')
    if (!token) {
      ElMessage.error('请先登录！')
      // 这里可以触发一个事件让 App.vue 跳转回登录页，简单起见我们直接刷新
      window.location.reload()
      return
    }

    messages.value.push({ role: 'user', content: query })
    const aiMessage: Message = { role: 'assistant', content: '' }
    messages.value.push(aiMessage)

    loading.value = true

    try {

      const response = await fetch('http://localhost:8000/api/conversations/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query })
      })

      // 处理 401 未登录/Token过期
      if (response.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('access_token')
        setTimeout(() => window.location.reload(), 1500)
        return
      }

      if (!response.body) return

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        messages.value[messages.value.length - 1].content += chunk
      }

    } catch (error) {
      console.error('Chat Error:', error)
      messages.value[messages.value.length - 1].content += '\n[网络错误，请稍后再试]'
    } finally {
      loading.value = false
    }
  }

  // 清空历史（注销时用）
  const clearChat = () => {
    messages.value = [{ role: 'assistant', content: '你好！我是你的大模型开发助手，有什么可以帮你的吗？' }]
  }

  return {
    messages,
    loading,
    sendMessage,
    clearChat
  }
}