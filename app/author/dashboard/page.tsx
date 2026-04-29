import Link from "next/link";
import { redirect } from "next/navigation";
import { ApiKeyManager } from "@/components/shared/presets/api-key-manager";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { hasSupabaseEnv } from "@/lib/supabase/env";

export default async function AuthorDashboardPage() {
  if (!hasSupabaseEnv()) {
    return (
      <div className="klyxe-container py-10">
        <div className="klyxe-panel p-6 text-sm text-zinc-300">
          configure supabase env to enable auth and dashboard features.
        </div>
      </div>
    );
  }

  const supabase = createSupabaseServerClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();

  if (!user) redirect("/auth/login");
  const { data: drafts } = await supabase
    .from("articles")
    .select("id,title,slug,status,created_at")
    .eq("author_id", user.id)
    .order("created_at", { ascending: false });

  return (
    <div className="klyxe-container py-10">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">author dashboard</h1>
          <p className="text-sm text-zinc-400">{user.email}</p>
        </div>
        <Link href="/author/editor/new" className="rounded border border-[#39ff14]/40 px-3 py-1 text-sm text-[#39ff14]">
          new article
        </Link>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <ApiKeyManager />
        <div className="klyxe-panel p-4">
          <h2 className="mb-2 text-lg font-semibold">my drafts</h2>
          <div className="space-y-2">
            {(drafts || []).map((draft) => (
              <div key={draft.id} className="rounded border border-zinc-800 px-3 py-2 text-sm">
                <p>{draft.title}</p>
                <p className="text-xs text-zinc-500">
                  {draft.status} · {draft.slug}
                </p>
              </div>
            ))}
            {!drafts?.length ? <p className="text-sm text-zinc-500">no drafts yet</p> : null}
          </div>
        </div>
      </div>
    </div>
  );
}
