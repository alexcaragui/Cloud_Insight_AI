import { Navigate, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const { t } = useTranslation()

  if (user) return <Navigate to="/" replace />

  async function handleLogin() {
    await login({ email: '', password: '' })
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-lg p-10 w-full max-w-sm flex flex-col items-center gap-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
          </svg>
        </div>

        <div className="text-center">
          <h1 className="text-xl font-bold text-slate-800">{t('login.title')}</h1>
          <p className="text-sm text-slate-500 mt-1">{t('login.subtitle')}</p>
        </div>

        <button
          onClick={handleLogin}
          className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors"
        >
          {t('login.button')}
        </button>
      </div>
    </div>
  )
}
