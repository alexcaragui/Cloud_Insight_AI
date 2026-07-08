import { useState } from 'react';
import { useLocation } from 'react-router-dom';

const PAGE_TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/upload': 'Upload',
  '/chat': 'AI Chat',
  '/reports': 'Reports',
};

export default function Header() {
  const location = useLocation();
  const [notifOpen, setNotifOpen] = useState(false);
  const title = PAGE_TITLES[location.pathname] ?? 'CloudInsight AI';

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 shadow-sm">
      {/* Page title */}
      <h1 className="text-lg font-semibold text-slate-800">{title}</h1>

      {/* Right actions */}
      <div className="flex items-center gap-4">
        {/* Notification bell */}
        <div className="relative">
          <button
            onClick={() => setNotifOpen(o => !o)}
            className="relative p-2 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full" />
          </button>

          {notifOpen && (
            <div className="absolute right-0 mt-1 w-72 bg-white rounded-xl shadow-lg border border-slate-200 p-4 z-50">
              <p className="text-sm font-medium text-slate-700 mb-2">Notifications</p>
              <p className="text-xs text-slate-400">No new notifications</p>
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="w-px h-8 bg-slate-200" />

        {/* Avatar */}
        <button className="flex items-center gap-2 hover:bg-slate-50 rounded-lg px-2 py-1 transition-colors">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-sm font-semibold">
            ZK
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-sm font-medium text-slate-700 leading-tight">User</p>
            <p className="text-xs text-slate-400 leading-tight">Admin</p>
          </div>
          <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    </header>
  );
}
