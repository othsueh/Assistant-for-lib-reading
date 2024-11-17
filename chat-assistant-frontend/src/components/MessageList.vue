<template>
  <div class="message-list" ref="messageContainer">
    <div v-for="(message, index) in chatStore.currentDialogMessages" 
        :key="`${index}-${message.content}`"
        :class="['message', message.role]">
      <div class="message-content" v-if="message.role === 'assistant'">
        <template v-for="(part, partIndex) in parseMessage(message.content)" :key="partIndex">
          <div v-if="part.type === 'thought_process'" class="thought-process-container">
            <button class="thought-header" @click="toggleThought(index, partIndex)">
              Thought process {{ expandedThoughts[`${index}-${partIndex}`] ? '▼' : '▶' }}
            </button>
            <div class="thought-process" :class="{ collapsed: !expandedThoughts[`${index}-${partIndex}`] }"
                 v-html="part.content">
            </div>
          </div>
          <pre v-else-if="part.type === 'code'" class="code-block">
            <code v-html="highlightCode(part.content, part.language)"></code>
          </pre>
          <div v-else class="answer" v-html="part.content">
          </div>
        </template>
      </div>
      <div class="message-content" v-else v-html="marked(message.content)">
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useChatStore } from '@/stores/chat'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/tokyo-night-dark.css'

const chatStore = useChatStore()
const messageContainer = ref<HTMLElement | null>(null)
const expandedThoughts = reactive<Record<string, boolean>>({})

// Create a custom renderer for marked
const renderer = new marked.Renderer()
renderer.code = (code: string, language: string | undefined) => {
  // Let the highlightCode function handle code blocks
  return code
}

marked.setOptions({
  renderer: renderer,
  highlight: null, // Disable marked's built-in highlighting
})

// Separate function to handle code highlighting
function highlightCode(code: string, language: string | undefined) {
  try {
    if (language && hljs.getLanguage(language)) {
      console.log('Highlighting code with language:', language)
      return hljs.highlight(code, { language }).value
    }
    console.log('Highlighting code with auto-detection')
    return hljs.highlightAuto(code).value
  } catch (e) {
    console.error('Error highlighting code:', e)
    return code // Return unhighlighted code if there's an error
  }
}

function toggleThought(messageIndex: number, partIndex: number) {
  const key = `${messageIndex}-${partIndex}`
  expandedThoughts[key] = !expandedThoughts[key]
}

function parseMessage(text: string) {
  const parts = []
  let currentText = text || ''

  // Parse thought process
  const thoughtMatch = currentText.match(/<thought_process>([\s\S]*?)(<\/thought_process>|$)/)
  if (thoughtMatch) {
    parts.push({
      type: 'thought_process',
      content: marked(thoughtMatch[1].trim())
    })
    currentText = currentText.replace(thoughtMatch[0], '')
  }

  // Parse code blocks with improved regex
  const codeBlockRegex = /<code(?:\s+lang=["']([^"']*)["'])?\s*>([\s\S]*?)(?:<\/code>|$)/g
  let codeMatch
  while ((codeMatch = codeBlockRegex.exec(currentText)) !== null) {
    const language = codeMatch[1] || ''
    parts.push({
      type: 'code',
      content: codeMatch[2].trim(),
      language: language
    })
    currentText = currentText.replace(codeMatch[0], '')
  }

  // Parse remaining content as answer
  if (currentText.trim()) {
    parts.push({
      type: 'answer',
      content: marked(currentText.trim())
    })
  }

  return parts
}

// Auto-scroll to bottom when new messages arrive
watch(
  () => chatStore.currentDialogMessages,
  (newMessages, oldMessages) => {
    if (newMessages.length > (oldMessages?.length || 0)) {
      const newMessageIndex = newMessages.length - 1
      expandedThoughts[`${newMessageIndex}-0`] = false
    }
    
    setTimeout(() => {
      if (messageContainer.value) {
        messageContainer.value.scrollTop = messageContainer.value.scrollHeight
      }
    }, 0)
  },
  { deep: true }
)
</script>
<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-left: 8rem;
  padding-right: 8rem;
}

.message {
  max-width: 100%;
  padding: 0.8rem;
  border-radius: 0.5rem;
  white-space: pre-wrap;
}

.message.user {
  align-self: flex-start;
  background-color: #413b61;
  color: white;
}
.thought-header {
  background: none;
  border: none;
  color: #413b61;
  cursor: pointer;
  padding: 0;
  margin-bottom: 0.5rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  width: 100%;
  text-align: left;
}

.thought-header:hover {
  opacity: 0.8;
}
.thought-process-container {
  position: relative;
  margin-bottom: 1rem;
}

.thought-process {
  background-color: #413b61;
  padding: 1rem;
  border-radius: 0.4rem;
  border-left: 4px solid #413b61;
  white-space: pre-wrap;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
  max-height: 1000px; /* Adjust based on your needs */
  color: #d4d4d4;
}

.thought-process.collapsed {
  max-height: 0;
  padding: 0;
  margin: 0;
  border: none;
}

.answer {
  background-color: #e5c9d7;
  padding: 1rem;
  border-radius: 0.4rem;
  margin-bottom: 1rem;
  white-space: pre-wrap;
}
.code-block {
  background-color: #161231;
  color: #d4d4d4;
  padding: 1rem;
  border-radius: 0.4rem;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  margin: 0 0 1rem 0;
}

.code-block code {
  display: block;
  line-height: 1.5;
}
:deep(.answer) {
  p {
    margin: 0;
  }
  
  code {
    background-color: #f0f0f0;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
  }

  pre code {
    background-color: transparent;
    padding: 0;
  }
}

:deep(.thought-process) {
  p {
    margin: 0;
  }
  
  code {
    background-color: #2d2d2d;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
  }
}
.message.assistant {
  background-color: #e5c9d7;
  color: black;
  box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.1);
}
</style>