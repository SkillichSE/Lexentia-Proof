import { loadLegacySummary } from "@/lib/legacy/loaders";

export default async function TrendsPage() {
  const summary = await loadLegacySummary();
  return (
    <div className="klyxe-container py-10">
      <h1 className="mb-6 text-2xl font-bold">trends snapshot</h1>
      <pre className="klyxe-panel overflow-x-auto p-4 text-xs text-zinc-300">
        {JSON.stringify(summary, null, 2)}
      </pre>
    </div>
  );
}
