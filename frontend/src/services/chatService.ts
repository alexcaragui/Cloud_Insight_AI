const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export function streamChat(
  model: string,
  messages: ChatMessage[],
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): () => void {
  const controller = new AbortController()

  fetch(`${BASE_URL}/ollama/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ model, messages }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok || !res.body) {
        onError(new Error(`Chat request failed: ${res.status}`))
        return
      }
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.message?.content) onToken(data.message.content)
              if (data.done) onDone()
            } catch {}
          }
        }
      }
      onDone()
    })
    .catch((err: Error) => {
      if (err.name !== 'AbortError') onError(err)
    })

  return () => controller.abort()
}
