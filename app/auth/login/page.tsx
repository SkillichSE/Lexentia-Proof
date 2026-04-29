import { AuthActions } from "@/components/shared/auth-actions";
import { hasSupabaseEnv } from "@/lib/supabase/env";

export default function LoginPage() {
  return (
    <div className="klyxe-container py-12">
      <div className="mx-auto max-w-md rounded-xl border border-zinc-800 bg-zinc-950/80 p-6">
        <h1 className="text-2xl font-semibold">author login</h1>
        <p className="mt-2 text-sm text-zinc-400">sign in with github or google to manage your articles.</p>
        {!hasSupabaseEnv() ? (
          <p className="mt-4 rounded border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-300">
            missing supabase env. configure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.
          </p>
        ) : (
          <div className="mt-5">
            <AuthActions />
          </div>
        )}
      </div>
    </div>
  );
}
