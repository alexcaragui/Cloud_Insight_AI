import { useTranslation } from 'react-i18next'

export default function Upload() {
  const { t } = useTranslation()
  return (
    <div className="p-4 text-2xl font-bold text-slate-800 dark:text-slate-100">
      {t('upload.title')}
    </div>
  )
}
