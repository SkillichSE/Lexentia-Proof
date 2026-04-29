import { redirect } from "next/navigation";
import { EditorWorkspace } from "@/components/author/editor-workspace";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { hasSupabaseEnv } from "@/lib/supabase/env";

export default async function AuthorEditorBySlugPage({ params }: { params: { slug: string } }) {
  if (!hasSupabaseEnv()) {
    return (
      <div className="klyxe-container py-10">
        <div className="klyxe-panel p-6 text-sm text-zinc-300">missing supabase env for protected editor.</div>
      </div>
    );
  }

  const supabase = createSupabaseServerClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  return (
    <div className="klyxe-container py-10">
      <h1 className="mb-4 text-2xl font-bold">editor / {params.slug}</h1>
      <EditorWorkspace slug={params.slug} />
    </div>
  );
}
