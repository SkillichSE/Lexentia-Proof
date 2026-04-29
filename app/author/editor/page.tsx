import Link from "next/link";

export default function AuthorEditorIndexPage() {
  return (
    <div className="klyxe-container py-10">
      <h1 className="mb-3 text-2xl font-bold">editor</h1>
      <p className="mb-4 text-sm text-zinc-400">open an editor slug to create or edit article content.</p>
      <Link href="/author/editor/new" className="text-[#39ff14] hover:underline">
        open new article editor
      </Link>
    </div>
  );
}
