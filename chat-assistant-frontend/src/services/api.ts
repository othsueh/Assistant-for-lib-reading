const API_BASE_URL = 'http://localhost:8000/api'

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
} as const

export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface Dialog {
  id: string
  messages: Message[]
}

export interface CreateDialogResponse {
  status: string
  dialog_id: string
  message: string
}

export interface DialogsResponse {
  dialogs: Array<{
    id: string
    messages: Message[]
  }>
}

export const api = {
  async createDialog(name: string): Promise<CreateDialogResponse> {
    const response = await fetch(`${API_BASE_URL}/dialogs/new`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify({ name }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create dialog')
    }
    
    return response.json()
  },

  async getDialogs(): Promise<DialogsResponse> {
    const response = await fetch(`${API_BASE_URL}/dialogs`,{headers: DEFAULT_HEADERS})
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch dialogs')
    }
    
    return response.json()
  },

  async sendMessage(message: string, dialogId: string): Promise<Response> {
    console.log('API: sending message:', message, 'to dialog:', dialogId) // Add debug log
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify({
        message,
        dialog_id: dialogId,
      }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to send message')
    }
    
    return response // Return the full response for streaming
  }
}