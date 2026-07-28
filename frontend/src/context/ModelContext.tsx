import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react'
import { listModels, pullModelStream, type OllamaModel, type PullProgress } from '../services/ollamaService'

const DEFAULT_MODEL = 'qwen2.5:7b'

interface ModelState {
  models: OllamaModel[]
  isLoading: boolean
  isPulling: boolean
  pullProgress: PullProgress | null
  isReady: boolean
  refresh: () => Promise<void>
  startPull: (name?: string) => void
}

const ModelContext = createContext<ModelState | null>(null)

export function ModelProvider({ children }: { children: React.ReactNode }) {
  const [models, setModels] = useState<OllamaModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isPulling, setIsPulling] = useState(false)
  const [pullProgress, setPullProgress] = useState<PullProgress | null>(null)
  const cancelPullRef = useRef<(() => void) | null>(null)
  const digestMapRef = useRef<Record<string, { completed: number; total: number }>>({})

  const refresh = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await listModels()
      setModels(data)
    } catch {
      // Ollama may not be reachable yet
    } finally {
      setIsLoading(false)
    }
  }, [])

  const isReady = models.some((m) =>
    m.name.startsWith(DEFAULT_MODEL.split(':')[0])
  )

  const startPull = useCallback(
    (name = DEFAULT_MODEL) => {
      if (isPulling) return
      digestMapRef.current = {}
      setIsPulling(true)
      setPullProgress({ status: 'starting' })
      cancelPullRef.current = pullModelStream(
        name,
        (progress) => {
          const map = digestMapRef.current
          if (progress.digest && progress.total != null) {
            map[progress.digest] = {
              completed: progress.completed ?? map[progress.digest]?.completed ?? 0,
              total: Math.max(progress.total, map[progress.digest]?.total ?? 0),
            }
          }
          const entries = Object.values(map)
          if (entries.length > 0 && progress.total != null) {
            const totalCompleted = entries.reduce((s, e) => s + e.completed, 0)
            const totalBytes = entries.reduce((s, e) => s + e.total, 0)
            setPullProgress({ status: progress.status, completed: totalCompleted, total: totalBytes, digest: progress.digest })
          } else {
            setPullProgress(progress)
          }
        },
        async () => {
          setIsPulling(false)
          setPullProgress(null)
          await refresh()
        },
        () => {
          setIsPulling(false)
          setPullProgress(null)
        },
      )
    },
    [isPulling, refresh],
  )

  useEffect(() => {
    refresh().then(() => {
      // checked after initial load — auto-pull if model is missing
    })
  }, [refresh])

  // Auto-pull once we know the model is missing
  useEffect(() => {
    if (!isLoading && !isReady && !isPulling) {
      startPull(DEFAULT_MODEL)
    }
  }, [isLoading, isReady, isPulling, startPull])

  return (
    <ModelContext.Provider value={{ models, isLoading, isPulling, pullProgress, isReady, refresh, startPull }}>
      {children}
    </ModelContext.Provider>
  )
}

export function useModel() {
  const ctx = useContext(ModelContext)
  if (!ctx) throw new Error('useModel must be used inside ModelProvider')
  return ctx
}

export { DEFAULT_MODEL }
