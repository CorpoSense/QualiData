<template>
  <BModal v-model="isOpen" size="fullscreen" hide-footer hide-header-close no-close-on-backdrop>
    <template #header>
      <div class="d-flex align-items-center gap-2 w-100">
        <i class="bi bi-chat-dots fs-5 text-primary"></i>
        <span class="fw-bold">AI Chat</span>
        <BBadge variant="light" class="text-muted border">
          <i class="bi bi-table me-1"></i>{{ columns.length }} cols · {{ totalRows }} rows
        </BBadge>
        <div class="ms-auto d-flex align-items-center gap-2">
          <BButton size="sm" variant="outline-secondary" @click="isOpen = false">
            <i class="bi bi-x-lg"></i>
          </BButton>
        </div>
      </div>
    </template>

    <div class="ai-chat-container d-flex">
      <!-- Left Sidebar: Chat History -->
      <div class="chat-sidebar">
        <div class="d-flex justify-content-between align-items-center mb-3 px-2">
          <span class="fw-bold small text-uppercase text-muted">Chats</span>
          <BButton size="sm" variant="outline-primary" @click="newChat" title="New chat">
            <i class="bi bi-plus-lg"></i>
          </BButton>
        </div>
        <div class="chat-list">
          <div
            v-for="session in sortedSessions"
            :key="session.id"
            class="chat-list-item"
            :class="{ active: session.id === activeSessionId }"
            @click="loadChat(session.id)"
          >
            <div class="d-flex justify-content-between align-items-start">
              <div class="text-truncate flex-grow-1" style="min-width: 0;">
                <div class="small fw-medium text-truncate">{{ session.title }}</div>
                <div class="text-muted" style="font-size: 0.7rem;">{{ formatTime(session.updatedAt) }}</div>
              </div>
              <button
                class="btn btn-sm btn-link text-muted p-0 ms-1"
                @click.stop="deleteChat(session.id)"
                title="Delete chat"
              >
                <i class="bi bi-trash3" style="font-size: 0.7rem;"></i>
              </button>
            </div>
          </div>
          <div v-if="sortedSessions.length === 0" class="text-center text-muted py-4 small">
            <i class="bi bi-chat-square d-block mb-1" style="font-size: 1.5rem;"></i>
            No chats yet
          </div>
        </div>
      </div>

      <!-- Right Panel: Active Chat -->
      <div class="chat-main d-flex flex-column">
        <!-- Chat Header -->
        <div class="chat-header d-flex align-items-center gap-2 px-3 py-2 border-bottom">
          <BFormSelect
            v-model="selectedAgentId"
            :options="agentOptions"
            size="sm"
            style="max-width: 280px;"
          ></BFormSelect>
          <BFormSelect
            v-model="contextRows"
            :options="contextRowOptions"
            size="sm"
            style="width: auto;"
            title="Number of dataset rows to include as context"
          ></BFormSelect>
          <BBadge v-if="selectedAgentId" variant="info" pill class="small">
            <i class="bi bi-robot me-1"></i>Active
          </BBadge>
          <div class="ms-auto d-flex align-items-center gap-1">
            <BButton
              size="sm"
              :variant="ttsEnabled ? 'primary' : 'outline-secondary'"
              @click="ttsEnabled = !ttsEnabled"
              title="Toggle text-to-speech for AI responses"
            >
              <i class="bi bi-volume-up"></i>
            </BButton>
            <BButton
              size="sm"
              variant="outline-secondary"
              @click="clearCurrentChat"
              title="Clear current chat messages"
            >
              <i class="bi bi-eraser"></i>
            </BButton>
          </div>
        </div>

        <!-- Messages Area -->
        <div class="chat-messages flex-grow-1 overflow-auto px-3 py-3" ref="messagesContainer">
          <!-- Welcome message when no messages -->
          <div v-if="messages.length === 0" class="text-center text-muted py-5">
            <i class="bi bi-robot d-block mb-2" style="font-size: 3rem; opacity: 0.3;"></i>
            <h6 class="text-muted">Start a conversation</h6>
            <p class="small">Select an AI Agent above and ask a question about your dataset.</p>
            <div class="d-flex flex-wrap justify-content-center gap-2 mt-3">
              <button
                v-for="suggestion in quickSuggestions"
                :key="suggestion"
                class="btn btn-sm btn-outline-secondary"
                @click="inputMessage = suggestion"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>

          <!-- Message bubbles -->
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="chat-message mb-3"
            :class="msg.role === 'user' ? 'user-message' : 'assistant-message'"
          >
            <div class="message-avatar">
              <i :class="msg.role === 'user' ? 'bi bi-person-fill' : 'bi bi-robot'" class="fs-6"></i>
            </div>
            <div class="message-content">
              <div class="message-bubble" :class="msg.role">
                <div v-if="msg.role === 'assistant'" v-html="renderMarkdown(msg.content)"></div>
                <div v-else style="white-space: pre-wrap;">{{ msg.content }}</div>
              </div>
              <div class="message-actions d-flex align-items-center gap-2 mt-1">
                <small class="text-muted" style="font-size: 0.65rem;">{{ formatTime(msg.timestamp) }}</small>
                <button
                  class="btn btn-sm btn-link text-muted p-0"
                  @click="copyToClipboard(msg.content)"
                  title="Copy message"
                >
                  <i class="bi bi-clipboard" style="font-size: 0.7rem;"></i>
                </button>
                <button
                  v-if="msg.role === 'assistant' && ttsEnabled"
                  class="btn btn-sm btn-link text-muted p-0"
                  @click="speak(msg.content)"
                  title="Read aloud"
                >
                  <i class="bi bi-volume-up" style="font-size: 0.7rem;"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Loading indicator -->
          <div v-if="loading" class="chat-message assistant-message mb-3">
            <div class="message-avatar">
              <i class="bi bi-robot fs-6"></i>
            </div>
            <div class="message-content">
              <div class="message-bubble assistant">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Error indicator -->
          <div v-if="error" class="alert alert-danger py-2 small mb-3">
            <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
          </div>
        </div>

        <!-- Input Bar -->
        <div class="chat-input-bar d-flex align-items-end gap-2 px-3 py-2 border-top">
          <div class="flex-grow-1">
            <textarea
              ref="inputRef"
              v-model="inputMessage"
              class="form-control form-control-sm"
              rows="1"
              placeholder="Ask about your data… (Enter to send, Shift+Enter for newline)"
              @keydown="onKeyDown"
              @input="autoResize"
              style="resize: none; max-height: 120px; overflow-y: auto;"
            ></textarea>
          </div>
          <BButton
            size="sm"
            variant="primary"
            :disabled="!canSend"
            @click="sendMessage"
            title="Send message"
          >
            <i class="bi bi-send"></i>
          </BButton>
        </div>
      </div>
    </div>
  </BModal>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { BModal, BButton, BFormSelect, BBadge } from 'bootstrap-vue-next'
import { getApiUrl } from '@/utils/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  datasetId: { type: String, default: '' },
  columns: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] },
  totalRows: { type: Number, default: 0 },
  agentOptions: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const apiUrl = getApiUrl()
const toast = useToast()

// State
const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const selectedAgentId = ref(null)
const contextRows = ref(10)
const ttsEnabled = ref(false)
const inputMessage = ref('')
const messages = ref([])
const loading = ref(false)
const error = ref('')
const messagesContainer = ref(null)
const inputRef = ref(null)
const activeSessionId = ref(null)
const chatSessions = ref([])

// Context row options
const contextRowOptions = [
  { value: 5, text: '5 rows context' },
  { value: 10, text: '10 rows context' },
  { value: 25, text: '25 rows context' },
  { value: 50, text: '50 rows context' },
  { value: 100, text: '100 rows context' },
]

// Quick suggestions for empty chat
const quickSuggestions = [
  'What patterns do you see in this data?',
  'Are there any data quality issues?',
  'Suggest cleaning operations for this dataset',
  'What columns might need type conversion?',
]

// Computed
const canSend = computed(() => {
  return inputMessage.value.trim() && selectedAgentId.value && !loading.value
})

const sortedSessions = computed(() => {
  return [...chatSessions.value]
    .filter(s => s.datasetId === props.datasetId)
    .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

// --- Chat Session Management (localStorage) ---

const STORAGE_KEY = 'ai-chat-sessions'
const MAX_SESSIONS = 50
const MAX_MESSAGES = 100

function loadSessions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      chatSessions.value = JSON.parse(raw)
    }
  } catch (e) {
    console.warn('Failed to load chat sessions:', e)
    chatSessions.value = []
  }
}

function saveSessions() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chatSessions.value))
  } catch (e) {
    console.warn('Failed to save chat sessions:', e)
  }
}

function newChat() {
  const session = {
    id: generateId(),
    title: 'New Chat',
    agentId: selectedAgentId.value,
    datasetId: props.datasetId,
    messages: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
  chatSessions.value.push(session)
  activeSessionId.value = session.id
  messages.value = []
  error.value = ''
  trimSessions()
  saveSessions()
  nextTick(() => focusInput())
}

function loadChat(sessionId) {
  const session = chatSessions.value.find(s => s.id === sessionId)
  if (!session) return
  activeSessionId.value = sessionId
  messages.value = [...session.messages]
  selectedAgentId.value = session.agentId
  error.value = ''
  nextTick(() => scrollToBottom())
}

function deleteChat(sessionId) {
  chatSessions.value = chatSessions.value.filter(s => s.id !== sessionId)
  if (activeSessionId.value === sessionId) {
    activeSessionId.value = null
    messages.value = []
  }
  saveSessions()
}

function clearCurrentChat() {
  if (!activeSessionId.value) return
  const session = chatSessions.value.find(s => s.id === activeSessionId.value)
  if (session) {
    session.messages = []
    session.updatedAt = new Date().toISOString()
  }
  messages.value = []
  saveSessions()
}

function updateActiveSession() {
  if (!activeSessionId.value) return
  const session = chatSessions.value.find(s => s.id === activeSessionId.value)
  if (!session) return
  session.messages = messages.value.slice(-MAX_MESSAGES)
  session.agentId = selectedAgentId.value
  session.updatedAt = new Date().toISOString()
  // Auto-title from first user message
  if (session.title === 'New Chat' && messages.value.length > 0) {
    const firstUserMsg = messages.value.find(m => m.role === 'user')
    if (firstUserMsg) {
      session.title = firstUserMsg.content.slice(0, 50) + (firstUserMsg.content.length > 50 ? '…' : '')
    }
  }
  saveSessions()
}

function trimSessions() {
  const datasetSessions = chatSessions.value.filter(s => s.datasetId === props.datasetId)
  if (datasetSessions.length > MAX_SESSIONS) {
    const toRemove = datasetSessions
      .sort((a, b) => new Date(a.updatedAt) - new Date(b.updatedAt))
      .slice(0, datasetSessions.length - MAX_SESSIONS)
      .map(s => s.id)
    chatSessions.value = chatSessions.value.filter(s => !toRemove.includes(s.id))
  }
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

// --- Message Sending ---

async function sendMessage() {
  if (!canSend.value) return

  const text = inputMessage.value.trim()
  if (!text) return

  // Ensure we have an active session
  if (!activeSessionId.value) {
    newChat()
  }

  // Add user message
  messages.value.push({
    role: 'user',
    content: text,
    timestamp: new Date().toISOString(),
  })
  inputMessage.value = ''
  error.value = ''
  resetTextareaHeight()
  updateActiveSession()
  nextTick(() => scrollToBottom())

  // Build conversation history (exclude current message)
  const conversationHistory = messages.value
    .slice(0, -1)
    .map(m => ({ role: m.role, content: m.content }))

  loading.value = true
  try {
    const body = {
      agent_id: selectedAgentId.value,
      message: text,
      conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined,
      dataset_id: props.datasetId || undefined,
      dataset_context_rows: contextRows.value,
    }

    const res = await fetch(`${apiUrl}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(body),
    })

    if (res.ok) {
      const data = await res.json()
      messages.value.push({
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
      })
      // Auto-speak if TTS enabled
      if (ttsEnabled.value) {
        speak(data.response)
      }
    } else {
      const err = await res.json().catch(() => ({}))
      error.value = err.detail || `Request failed (${res.status})`
    }
  } catch (e) {
    error.value = e.message || 'Network error'
  } finally {
    loading.value = false
    updateActiveSession()
    nextTick(() => scrollToBottom())
  }
}

// --- Keyboard Handling ---

function onKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// --- Auto-resize Textarea ---

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

function resetTextareaHeight() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
}

// --- Scroll ---

function scrollToBottom() {
  const container = messagesContainer.value
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

function focusInput() {
  inputRef.value?.focus()
}

// --- Text-to-Speech ---

function speak(text) {
  if (!window.speechSynthesis) return
  // Cancel any ongoing speech
  window.speechSynthesis.cancel()
  // Strip HTML/markdown for speech
  const plainText = text
    .replace(/```[\s\S]*?```/g, ' code block ')
    .replace(/`[^`]+`/g, ' code ')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/#{1,6}\s/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[|>_-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  const utterance = new SpeechSynthesisUtterance(plainText)
  utterance.rate = 1.0
  utterance.pitch = 1.0
  window.speechSynthesis.speak(utterance)
}

// --- Markdown Rendering ---

function renderMarkdown(text) {
  if (!text) return ''
  let html = escapeHtml(text)

  // Code blocks (```lang\n...\n```)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre class="code-block"><code class="language-${lang || 'text'}">${code}</code></pre>`
  })

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')

  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')

  // Italic
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  // Headers
  html = html.replace(/^#### (.+)$/gm, '<h6>$1</h6>')
  html = html.replace(/^### (.+)$/gm, '<h5>$1</h5>')
  html = html.replace(/^## (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^# (.+)$/gm, '<h3>$1</h3>')

  // Unordered lists
  html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')

  // Tables (simple markdown tables)
  html = renderMarkdownTables(html)

  // Line breaks (preserve newlines outside of pre blocks)
  html = html.replace(/\n/g, '<br>')

  // Clean up excessive <br> inside pre blocks
  html = html.replace(/<pre class="code-block">([\s\S]*?)<\/pre>/g, (match, content) => {
    return `<pre class="code-block">${content.replace(/<br>/g, '\n')}</pre>`
  })

  return html
}

function renderMarkdownTables(html) {
  // Match table-like patterns: | header | header |\n| --- | --- |\n| cell | cell |
  const tableRegex = /((?:^\| .+$\n?)+)/gm
  return html.replace(tableRegex, (match) => {
    const rows = match.trim().split('\n').filter(r => r.trim())
    if (rows.length < 2) return match

    const parsedRows = rows.map(r =>
      r.split('|').map(c => c.trim()).filter(c => c !== '')
    )

    // Check if second row is a separator
    const isSeparator = parsedRows.length > 1 &&
      parsedRows[1].every(cell => /^[-:]+$/.test(cell))

    let tableHtml = '<table class="table table-sm table-bordered small mb-2">'
    let startRow = 0

    if (parsedRows.length > 0) {
      tableHtml += '<thead><tr>'
      for (const cell of parsedRows[0]) {
        tableHtml += `<th>${cell}</th>`
      }
      tableHtml += '</tr></thead>'
      startRow = isSeparator ? 2 : 1
    }

    if (startRow < parsedRows.length) {
      tableHtml += '<tbody>'
      for (let i = startRow; i < parsedRows.length; i++) {
        tableHtml += '<tr>'
        for (const cell of parsedRows[i]) {
          tableHtml += `<td>${cell}</td>`
        }
        tableHtml += '</tr>'
      }
      tableHtml += '</tbody>'
    }

    tableHtml += '</table>'
    return tableHtml
  })
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// --- Utilities ---

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(
    () => toast.success('Copied to clipboard'),
    () => toast.error('Failed to copy')
  )
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// --- Watchers ---

// When modal opens, load sessions and ensure active chat
watch(() => props.modelValue, (val) => {
  if (val) {
    loadSessions()
    if (!activeSessionId.value && sortedSessions.value.length > 0) {
      loadChat(sortedSessions.value[0].id)
    } else if (!activeSessionId.value) {
      newChat()
    }
    nextTick(() => focusInput())
  } else {
    // Cancel speech when closing
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
  }
})

// When datasetId changes, reset chat state
watch(() => props.datasetId, () => {
  activeSessionId.value = null
  messages.value = []
  error.value = ''
  loadSessions()
  if (sortedSessions.value.length > 0) {
    loadChat(sortedSessions.value[0].id)
  }
})
</script>

<style scoped>
.ai-chat-container {
  height: calc(100vh - 120px);
  min-height: 400px;
}

/* Left Sidebar */
.chat-sidebar {
  width: 240px;
  min-width: 240px;
  border-right: 1px solid #e2e8f0;
  padding: 12px 8px;
  overflow-y: auto;
  background: #f8fafc;
}

.chat-list-item {
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 2px;
  transition: background 0.15s;
}

.chat-list-item:hover {
  background: #e2e8f0;
}

.chat-list-item.active {
  background: #dbeafe;
  border-left: 3px solid #3b82f6;
}

/* Right Panel */
.chat-main {
  flex: 1;
  min-width: 0;
}

/* Chat Header */
.chat-header {
  background: #fff;
  flex-shrink: 0;
}

/* Messages Area */
.chat-messages {
  background: #f1f5f9;
  flex: 1;
  min-height: 0;
}

/* Message Bubbles */
.chat-message {
  display: flex;
  gap: 8px;
  max-width: 85%;
}

.chat-message.user-message {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 0.8rem;
}

.user-message .message-avatar {
  background: #3b82f6;
  color: #fff;
}

.assistant-message .message-avatar {
  background: #e2e8f0;
  color: #475569;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 0.875rem;
  line-height: 1.5;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message-bubble.user {
  background: #3b82f6;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant {
  background: #fff;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
}

/* Markdown Styles inside assistant bubbles */
.message-bubble.assistant :deep(h3) {
  font-size: 1.1rem;
  margin: 8px 0 4px;
}

.message-bubble.assistant :deep(h4) {
  font-size: 1rem;
  margin: 6px 0 3px;
}

.message-bubble.assistant :deep(h5) {
  font-size: 0.95rem;
  margin: 4px 0 2px;
}

.message-bubble.assistant :deep(h6) {
  font-size: 0.9rem;
  margin: 4px 0 2px;
}

.message-bubble.assistant :deep(ul),
.message-bubble.assistant :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}

.message-bubble.assistant :deep(li) {
  margin: 2px 0;
}

.message-bubble.assistant :deep(.code-block) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 10px 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.8rem;
  margin: 8px 0;
  line-height: 1.4;
}

.message-bubble.assistant :deep(.inline-code) {
  background: #f1f5f9;
  color: #dc2626;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 0.82rem;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.message-bubble.assistant :deep(table) {
  font-size: 0.8rem;
}

.message-bubble.assistant :deep(table th) {
  background: #f1f5f9;
}

.message-bubble.assistant :deep(strong) {
  font-weight: 600;
}

/* Message Actions */
.message-actions {
  opacity: 0;
  transition: opacity 0.15s;
}

.chat-message:hover .message-actions {
  opacity: 1;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #94a3b8;
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* Input Bar */
.chat-input-bar {
  background: #fff;
  flex-shrink: 0;
}

.chat-input-bar textarea {
  border-radius: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .chat-sidebar {
    display: none;
  }

  .chat-message {
    max-width: 95%;
  }
}
</style>
