import type { ReactNode } from "react";

type ArticleLayoutProps = {
  title: string;
  author: string;
  tags: string[];
  children: ReactNode;
};

export function ArticleLayout({ title, author, tags, children }: ArticleLayoutProps) {
  return (
    <div className="klyxe-container py-10">
      <header className="mb-6 border-b border-zinc-800 pb-6">
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        <p className="mt-2 text-sm text-zinc-400">by {author}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span key={tag} className="rounded border border-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
              {tag}
            </span>
          ))}
        </div>
      </header>
      {children}
    </div>
  );
}
