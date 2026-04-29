import { promises as fs } from "node:fs";
import path from "node:path";
import matter from "gray-matter";

export type LocalArticle = {
  slug: string;
  title: string;
  author: string;
  tags: string[];
  status: "draft" | "published";
  interactive: boolean;
  content: string;
};

const articleRoots = [path.join(process.cwd(), "content"), path.join(process.cwd(), "content", "articles")];

function normalize(raw: Partial<LocalArticle>, slug: string, content: string): LocalArticle {
  return {
    slug,
    title: raw.title || slug,
    author: raw.author || "unknown",
    tags: Array.isArray(raw.tags) ? raw.tags : [],
    status: raw.status === "draft" ? "draft" : "published",
    interactive: Boolean(raw.interactive),
    content
  };
}

export async function listLocalArticles(): Promise<LocalArticle[]> {
  const collected: LocalArticle[] = [];
  for (const root of articleRoots) {
    let files: string[] = [];
    try {
      files = await fs.readdir(root);
    } catch {
      continue;
    }
    const mdxFiles = files.filter((f) => f.endsWith(".mdx"));
    for (const file of mdxFiles) {
      const slug = file.replace(/\.mdx$/, "");
      const fullPath = path.join(root, file);
      const raw = await fs.readFile(fullPath, "utf-8");
      const parsed = matter(raw);
      collected.push(normalize(parsed.data as Partial<LocalArticle>, slug, parsed.content));
    }
  }
  const unique = new Map<string, LocalArticle>();
  collected.forEach((article) => unique.set(article.slug, article));
  return Array.from(unique.values()).sort((a, b) => a.slug.localeCompare(b.slug));
}

export async function getLocalArticle(slug: string): Promise<LocalArticle | null> {
  for (const root of articleRoots) {
    try {
      const fullPath = path.join(root, `${slug}.mdx`);
      const raw = await fs.readFile(fullPath, "utf-8");
      const parsed = matter(raw);
      return normalize(parsed.data as Partial<LocalArticle>, slug, parsed.content);
    } catch {
      continue;
    }
  }
  return null;
}
