import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import { mdxPresetComponents } from "@/lib/ai-runtime";

type MdxRendererProps = {
  source: string;
};

export function MdxRenderer({ source }: MdxRendererProps) {
  return (
    <article className="prose prose-invert max-w-none prose-zinc">
      <MDXRemote
        source={source}
        components={mdxPresetComponents}
        options={{ mdxOptions: { remarkPlugins: [remarkGfm] } }}
      />
    </article>
  );
}
