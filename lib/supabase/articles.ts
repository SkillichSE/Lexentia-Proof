import { createSupabaseServerClient } from "@/lib/supabase/server";

export type ArticleRecord = {
  id: string;
  author_id: string;
  title: string;
  slug: string;
  content_mdx: string;
  tags: string[];
  status: "draft" | "published";
  created_at: string;
};

export async function getArticles() {
  const supabase = createSupabaseServerClient();
  const { data, error } = await supabase
    .from("articles")
    .select("*")
    .eq("status", "published")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return (data || []) as ArticleRecord[];
}

export async function saveArticle(input: {
  id?: string;
  title: string;
  slug: string;
  content_mdx: string;
  tags: string[];
  status: "draft" | "published";
}) {
  const supabase = createSupabaseServerClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();
  if (!user) throw new Error("unauthorized");

  const payload = {
    id: input.id,
    author_id: user.id,
    title: input.title,
    slug: input.slug,
    content_mdx: input.content_mdx,
    tags: input.tags,
    status: input.status
  };

  const { data, error } = await supabase.from("articles").upsert(payload).select("*").single();
  if (error) throw error;
  return data as ArticleRecord;
}

