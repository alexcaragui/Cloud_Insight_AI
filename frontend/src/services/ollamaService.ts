const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export interface OllamaModel {
  name: string
  size: number
  modified_at: string
  digest: string
}

export async function listModels(): Promise<OllamaModel[]> {
  const res = await fetch(`${BASE_URL}/ollama/models`, { headers: authHeaders() })
  if (!res.ok) throw new Error(`Failed to list models: ${res.status}`)
  const data = await res.json()
  return (data.models ?? []) as OllamaModel[]
}

export async function deleteModel(name: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/ollama/models/${encodeURIComponent(name)}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to delete model: ${res.status}`)
}

export interface PullProgress {
  status: string
  completed?: number
  total?: number
  digest?: string
}

export function pullModelStream(
  name: string,
  onProgress: (data: PullProgress) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): () => void {
  const controller = new AbortController()

  fetch(`${BASE_URL}/ollama/models/pull`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ name }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok || !res.body) {
        onError(new Error(`Pull failed: ${res.status}`))
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
              onProgress(JSON.parse(line.slice(6)) as PullProgress)
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
