"use client";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export async function uploadModelAsset(file: File) {
  const supabase = createSupabaseBrowserClient();
  const key = `models/${Date.now()}-${file.name}`;
  const { error } = await supabase.storage.from("models").upload(key, file, { upsert: false });
  if (error) throw error;
  const { data } = supabase.storage.from("models").getPublicUrl(key);
  return data.publicUrl;
}
