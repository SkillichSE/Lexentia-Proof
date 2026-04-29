import { ArticleCard } from "@/components/shared/article-card";
import { listLocalArticles } from "@/lib/mdx/articles";

export default async function HomePage() {
  const articles = await listLocalArticles();

  return (
    <div className="klyxe-container py-10">
      <section className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">interactive ai articles</h1>
        <p className="mt-2 max-w-2xl text-zinc-400">
          klyxe blends long-form ai writing with runnable demos that execute directly in the reader browser.
        </p>
      </section>
      <section className="grid gap-4 md:grid-cols-2">
        {articles.map((article) => (
          <ArticleCard
            key={article.slug}
            title={article.title}
            slug={article.slug}
            author={article.author}
            tags={article.tags}
            isInteractive={article.interactive}
          />
        ))}
      </section>
    </div>
  );
}
