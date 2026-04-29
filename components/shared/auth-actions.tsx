"use client";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export function AuthActions() {
  const signIn = async (provider: "google" | "github") => {
    const supabase = createSupabaseBrowserClient();
    await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/author/dashboard`
      }
    });
  };

  return (
    <div className="flex flex-wrap gap-2">
      <button className="rounded border border-zinc-700 px-3 py-2 text-sm" onClick={() => signIn("github")}>
        continue with github
      </button>
      <button className="rounded border border-zinc-700 px-3 py-2 text-sm" onClick={() => signIn("google")}>
        continue with google
      </button>
    </div>
  );
}
