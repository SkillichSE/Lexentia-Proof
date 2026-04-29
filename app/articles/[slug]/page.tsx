import { notFound } from "next/navigation";
import { ArticleLayout } from "@/components/shared/article-layout";
import { MdxRenderer } from "@/components/shared/mdx-renderer";
import { getLocalArticle, listLocalArticles } from "@/lib/mdx/articles";

export async function generateStaticParams() {
  const articles = await listLocalArticles();
  return articles.map((article) => ({ slug: article.slug }));
}

export default async function ArticleBySlugPage({ params }: { params: { slug: string } }) {
  const article = await getLocalArticle(params.slug);
  if (!article || article.status !== "published") notFound();

  return (
    <ArticleLayout title={article.title} author={article.author} tags={article.tags}>
      <MdxRenderer source={article.content} />
    </ArticleLayout>
  );
}
