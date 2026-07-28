const _apiBase = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')

// Convert http(s) base URL to ws(s); handle relative paths too
const WS_BASE = _apiBase.startsWith('http')
  ? _apiBase.replace(/^http/, 'ws')
  : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}${_apiBase}`

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

type Handlers = {
  onToken: (token: string) => void
  onDone: () => void
  onError: (msg: string) => void
}

export class ChatSocket {
  private ws: WebSocket
  private handlers: Handlers | null = null
  private pendingPayload: string | null = null

  constructor(onConnectionError: (msg: string) => void) {
    const token = localStorage.getItem('token')
    const url = token
      ? `${WS_BASE}/ollama/chat/ws?token=${encodeURIComponent(token)}`
      : `${WS_BASE}/ollama/chat/ws`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      if (this.pendingPayload !== null) {
        this.ws.send(this.pendingPayload)
        this.pendingPayload = null
      }
    }

    this.ws.onmessage = (e) => {
      if (!this.handlers) return
      try {
        const msg = JSON.parse(e.data as string) as { type: string; content?: string; message?: string }
        if (msg.type === 'token') this.handlers.onToken(msg.content ?? '')
        else if (msg.type === 'done') this.handlers.onDone()
        else if (msg.type === 'error') this.handlers.onError(msg.message ?? 'Unknown error')
      } catch {}
    }

    this.ws.onerror = () => onConnectionError('WebSocket connection error')
  }

  send(model: string, messages: ChatMessage[], handlers: Handlers) {
    this.handlers = handlers
    const payload = JSON.stringify({ model, messages })
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(payload)
    } else {
      // Queue until the connection is open
      this.pendingPayload = payload
    }
  }

  close() {
    this.ws.close()
  }
}
