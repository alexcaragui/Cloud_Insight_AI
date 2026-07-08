export default function Footer() {
  return (
    <footer className="h-10 bg-white border-t border-slate-200 flex items-center justify-between px-6 shrink-0">
      <p className="text-xs text-slate-400">
        &copy; {new Date().getFullYear()} CloudInsight AI. All rights reserved.
      </p>
      <div className="flex items-center gap-4">
        <span className="text-xs text-slate-300">v1.0.0</span>
        <span className="flex items-center gap-1.5 text-xs text-emerald-500 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          All systems operational
        </span>
      </div>
    </footer>
  );
}
