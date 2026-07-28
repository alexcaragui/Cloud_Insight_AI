import { Link, Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { useModel } from '../../context/ModelContext';

function DownloadBanner() {
  const { isPulling, pullProgress } = useModel();
  if (!isPulling) return null;
  const pct =
    pullProgress?.total && pullProgress?.completed
      ? Math.round((pullProgress.completed / pullProgress.total) * 100)
      : null;
  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-blue-600 text-white text-xs">
      <svg className="w-3.5 h-3.5 animate-spin shrink-0" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span className="flex-1 truncate">
        Downloading model{pullProgress?.status ? `: ${pullProgress.status}` : '…'}
      </span>
      {pct !== null && (
        <span className="font-mono font-semibold shrink-0">{pct}%</span>
      )}
    </div>
  );
}

function FloatingChatButton() {
  const { isReady } = useModel();
  if (!isReady) return null;
  return (
    <Link
      to="/chat"
      className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-900/40 flex items-center justify-center transition-all hover:scale-105 active:scale-95"
      title="Open AI Chat"
    >
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    </Link>
  );
}

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <DownloadBanner />
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
        <Footer />
      </div>
      <FloatingChatButton />
    </div>
  );
}
