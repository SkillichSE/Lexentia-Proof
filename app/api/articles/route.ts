import { NextResponse } from "next/server";
import { getArticles, saveArticle } from "@/lib/supabase/articles";

export async function GET() {
  try {
    const articles = await getArticles();
    return NextResponse.json({ articles });
  } catch (error) {
    const message = error instanceof Error ? error.message : "failed to read articles";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      title: string;
      slug: string;
      content_mdx: string;
      tags: string[];
      status: "draft" | "published";
      id?: string;
    };
    const article = await saveArticle(body);
    return NextResponse.json({ article });
  } catch (error) {
    const message = error instanceof Error ? error.message : "failed to save article";
    const status = message.includes("unauthorized") ? 401 : 500;
    return NextResponse.json({ error: message }, { status });
  }
}
