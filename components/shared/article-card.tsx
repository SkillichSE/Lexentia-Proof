import Link from "next/link";

type ArticleCardProps = {
  title: string;
  slug: string;
  author: string;
  tags: string[];
  isInteractive?: boolean;
};

export function ArticleCard({ title, slug, author, tags, isInteractive = false }: ArticleCardProps) {
  return (
    <article className="klyxe-panel p-4">
      <div className="mb-2 flex items-center justify-between gap-3">
        <h3 className="text-base font-semibold">{title}</h3>
        {isInteractive ? (
          <span className="rounded-full border border-[#39ff14]/40 px-2 py-0.5 text-xs text-[#39ff14]">
            interactive
          </span>
        ) : null}
      </div>
      <p className="mb-3 text-xs text-zinc-400">by {author}</p>
      <div className="mb-4 flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span key={tag} className="rounded border border-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
            {tag}
          </span>
        ))}
      </div>
      <Link href={`/articles/${slug}`} className="text-sm text-[#39ff14] hover:underline">
        open article
      </Link>
    </article>
  );
}
