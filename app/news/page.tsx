import { loadLegacyNews } from "@/lib/legacy/loaders";

export default async function NewsPage() {
  const news = await loadLegacyNews();
  return (
    <div className="klyxe-container py-10">
      <h1 className="mb-6 text-2xl font-bold">news feed</h1>
      <div className="space-y-3">
        {news.slice(0, 20).map((item, i) => (
          <article key={`${item.title || "item"}-${i}`} className="klyxe-panel p-4">
            <p className="text-xs text-zinc-500">{item.date || "unknown date"}</p>
            <h2 className="mt-1 text-base font-semibold">{item.title || "untitled update"}</h2>
            <p className="mt-2 text-sm text-zinc-400">{item.summary || "no summary"}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
