import Link from "next/link";
import { CanvasPreview } from "@/components/shared/presets/canvas-preview";
import { LlmChat } from "@/components/shared/presets/llm-chat";

export default function LabPage() {
  return (
    <div className="klyxe-container py-10">
      <section className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">klyxe lab</h1>
        <p className="mt-2 max-w-2xl text-zinc-400">
          interactive ai runtime with mdx-ready presets. author login and publishing are available in the dashboard.
        </p>
        <div className="mt-4 flex gap-3">
          <Link href="/dashboard" className="rounded border border-[#39ff14]/40 px-3 py-1 text-sm text-[#39ff14]">
            open dashboard
          </Link>
          <Link href="/articles/test" className="rounded border border-zinc-700 px-3 py-1 text-sm">
            open mdx demo article
          </Link>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="klyxe-panel p-4">
          <h2 className="mb-3 text-lg font-semibold">canvas preset</h2>
          <CanvasPreview />
        </div>
        <div className="klyxe-panel p-4">
          <h2 className="mb-3 text-lg font-semibold">llm chat preset</h2>
          <LlmChat provider="openai" />
        </div>
      </section>
    </div>
  );
}
