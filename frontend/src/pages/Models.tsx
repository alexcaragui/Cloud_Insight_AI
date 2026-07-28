import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useModel, DEFAULT_MODEL } from '../context/ModelContext'
import { deleteModel } from '../services/ollamaService'

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
}

function PullProgressBar({ status, completed, total }: { status: string; completed?: number; total?: number }) {
  const pct = total && completed ? Math.round((completed / total) * 100) : null
  return (
    <div className="mt-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-slate-400 truncate">{status}</span>
        {pct !== null && <span className="text-xs text-blue-400 font-mono ml-2">{pct}%</span>}
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-300"
          style={{
            width: pct !== null ? `${pct}%` : '40%',
            animation: pct === null ? 'pulse 1.5s ease-in-out infinite' : 'none',
          }}
        />
      </div>
    </div>
  )
}

export default function Models() {
  const { t } = useTranslation()
  const { models, isLoading, isPulling, pullProgress, refresh, startPull } = useModel()
  const [deletingName, setDeletingName] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)

  async function handleDelete(name: string) {
    if (confirmDelete !== name) {
      setConfirmDelete(name)
      return
    }
    setConfirmDelete(null)
    setDeletingName(name)
    try {
      await deleteModel(name)
      await refresh()
    } finally {
      setDeletingName(null)
    }
  }

  const installedNames = new Set(models.map((m) => m.name))
  const isDefaultInstalled = models.some((m) =>
    m.name.startsWith(DEFAULT_MODEL.split(':')[0])
  )
  const defaultModelEntry = models.find((m) =>
    m.name.startsWith(DEFAULT_MODEL.split(':')[0])
  )
  const otherModels = models.filter(
    (m) => !m.name.startsWith(DEFAULT_MODEL.split(':')[0])
  )

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">{t('models.title')}</h1>
        <p className="text-sm text-slate-500 mt-1">{t('models.subtitle')}</p>
      </div>

      {/* Default model card */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shrink-0">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-slate-800 dark:text-slate-100 truncate">{DEFAULT_MODEL}</p>
              <p className="text-xs text-slate-400">Qwen 2.5 · 7B parameters</p>
              {defaultModelEntry && (
                <p className="text-xs text-slate-400">{formatBytes(defaultModelEntry.size)}</p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {isDefaultInstalled ? (
              <>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  {t('models.installed')}
                </span>
                <button
                  onClick={() => handleDelete(defaultModelEntry!.name)}
                  disabled={deletingName === defaultModelEntry?.name}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50"
                >
                  {confirmDelete === defaultModelEntry?.name
                    ? t('models.confirmDelete')
                    : deletingName === defaultModelEntry?.name
                    ? t('models.deleting')
                    : t('models.delete')}
                </button>
              </>
            ) : isPulling ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                {t('models.downloading')}
              </span>
            ) : (
              <button
                onClick={() => startPull(DEFAULT_MODEL)}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              >
                {t('models.install')}
              </button>
            )}
          </div>
        </div>

        {isPulling && !installedNames.has(defaultModelEntry?.name ?? '') && pullProgress && (
          <PullProgressBar
            status={pullProgress.status}
            completed={pullProgress.completed}
            total={pullProgress.total}
          />
        )}
      </div>

      {/* Other installed models */}
      {otherModels.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">
            {t('models.otherInstalled')}
          </h2>
          <div className="space-y-3">
            {otherModels.map((model) => (
              <div
                key={model.name}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm flex items-center justify-between gap-4"
              >
                <div className="min-w-0">
                  <p className="font-medium text-slate-800 dark:text-slate-100 truncate text-sm">{model.name}</p>
                  <p className="text-xs text-slate-400">{formatBytes(model.size)}</p>
                </div>
                <button
                  onClick={() => handleDelete(model.name)}
                  disabled={deletingName === model.name}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50 shrink-0"
                >
                  {confirmDelete === model.name
                    ? t('models.confirmDelete')
                    : deletingName === model.name
                    ? t('models.deleting')
                    : t('models.delete')}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-12 text-slate-400 text-sm gap-2">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          {t('models.loading')}
        </div>
      )}

      {!isLoading && models.length === 0 && !isPulling && (
        <p className="text-center py-12 text-slate-400 text-sm">{t('models.noModels')}</p>
      )}

      <div className="flex justify-end">
        <button
          onClick={refresh}
          className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 flex items-center gap-1.5 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {t('models.refresh')}
        </button>
      </div>
    </div>
  )
}
