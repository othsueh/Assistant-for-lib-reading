import { defineStore } from 'pinia'
import { api, type Message, type Dialog } from '@/services/api'

export const useChatStore = defineStore('chat', {
  state: () => ({
    dialogs: [] as Dialog[],
    currentDialogId: 'default',
    isLoading: false,
    currentStreamedMessage: ''
  }),

  getters: {
    currentDialog: (state) => 
      state.dialogs.find(d => d.id === state.currentDialogId) || { id: state.currentDialogId, messages: [] },
    
    currentDialogMessages: (state) => {
      const dialog = state.dialogs.find(d => d.id === state.currentDialogId)
      return dialog?.messages || []
    }
  },

  actions: {
    async sendMessage(message: string) {
      console.log('Sending message:', message)
      this.isLoading = true
      
      this.addMessage({
        role: 'user',
        content: message
      })

      try {
        const response = await api.sendMessage(message, this.currentDialogId)
        
        if (!response.body) {
          throw new Error('No response stream')
        }
        
        this.addMessage({
          role: 'assistant',
          content: ''
        })
        
        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        while (true) {
          const { value, done } = await reader.read()
          if (done) break
          
          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                if (data.chunk) {
                  // Update the message directly with the new chunk
                  const dialog = this.dialogs.find(d => d.id === this.currentDialogId)
                  if (dialog) {
                    const lastAssistantMessage = dialog.messages.findLast(m => m.role === 'assistant')
                    if (lastAssistantMessage) {
                      lastAssistantMessage.content += data.chunk
                    }
                  }
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e)
              }
            }
          }
        }
      } catch (error) {
        console.error('Error sending message:', error)
      } finally {
        this.isLoading = false
      }
    },

    addMessage(message: Message) {
      const dialog = this.dialogs.find(d => d.id === this.currentDialogId)
      if (dialog) {
        dialog.messages.push(message)
      } else {
        this.dialogs.push({
          id: this.currentDialogId,
          messages: [message]
        })
      }
    },

    updateLastAssistantMessage(content: string) {
      const dialog = this.dialogs.find(d => d.id === this.currentDialogId)
      if (dialog) {
        const lastAssistantMessage = dialog.messages.findLast(m => m.role === 'assistant')
        if (lastAssistantMessage) {
          // Append the new content instead of replacing it
          lastAssistantMessage.content = content
        } else {
          // If no assistant message exists, create a new one
          dialog.messages.push({
            role: 'assistant',
            content
          })
        }
      }
    },

    setCurrentDialog(dialogId: string) {
      this.currentDialogId = dialogId
    },

    async createNewDialog(name: string) {
      try {
        const response = await api.createDialog(name)
        await this.loadDialogs()
        this.setCurrentDialog(response.dialog_id)
        return response
      } catch (error) {
        console.error('Error creating dialog:', error)
      }
    },

    async loadDialogs() {
      try {
        const { dialogs } = await api.getDialogs()
        this.dialogs = dialogs
      } catch (error) {
        console.error('Error loading dialogs:', error)
      }
    }
  }
})