"use client";

import type { ReactNode } from "react";

type AIDemoShellProps = {
  title: string;
  loading: boolean;
  progress: number;
  error: string | null;
  children: ReactNode;
};

export function AIDemoShell({ title, loading, progress, error, children }: AIDemoShellProps) {
  return (
    <div className="my-6 rounded-xl border border-zinc-800 bg-zinc-950/80 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-zinc-200">{title}</h3>
        {loading ? <span className="text-xs text-zinc-400">loading {Math.round(progress)}%</span> : null}
      </div>
      {loading ? (
        <div className="mb-3 h-2 w-full rounded bg-zinc-800">
          <div className="h-2 rounded bg-[#39ff14] transition-all" style={{ width: `${progress}%` }} />
        </div>
      ) : null}
      {error ? <div className="mb-3 rounded border border-red-500/30 bg-red-500/10 p-2 text-sm text-red-300">{error}</div> : null}
      {children}
    </div>
  );
}
