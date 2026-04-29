import { ArticleCard } from "@/components/shared/article-card";
import { listLocalArticles } from "@/lib/mdx/articles";

export default async function ArticlesPage() {
  const articles = await listLocalArticles();
  return (
    <div className="klyxe-container py-10">
      <h1 className="mb-6 text-2xl font-bold">articles</h1>
      <div className="grid gap-4 md:grid-cols-2">
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
      </div>
    </div>
  );
}
