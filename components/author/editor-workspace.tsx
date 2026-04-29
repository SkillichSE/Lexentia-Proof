"use client";

import { useMemo, useState } from "react";
import { MdxRenderer } from "@/components/shared/mdx-renderer";
import { uploadModelAsset } from "@/lib/supabase/upload-model-asset";

type EditorWorkspaceProps = {
  slug?: string;
  initialTitle?: string;
  initialContent?: string;
};

export function EditorWorkspace({ slug = "new-article", initialTitle = "", initialContent = "" }: EditorWorkspaceProps) {
  const [title, setTitle] = useState(initialTitle);
  const [content, setContent] = useState(initialContent);
  const [status, setStatus] = useState<"draft" | "published">("draft");
  const [assetUrl, setAssetUrl] = useState("");
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState("");
  const previewSource = useMemo(() => (content.trim() ? content : "add mdx content for preview"), [content]);

  const saveDraft = () => {
    void persist("draft");
  };

  const publish = () => {
    void persist("published");
  };

  const persist = async (targetStatus: "draft" | "published") => {
    setNotice("");
    try {
      const response = await fetch("/api/articles", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          title,
          slug,
          content_mdx: content,
          tags: [],
          status: targetStatus
        })
      });
      if (!response.ok) throw new Error(`save failed ${response.status}`);
      setStatus(targetStatus);
      setNotice(targetStatus === "draft" ? "draft saved" : "article published");
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "save failed");
    }
  };

  const uploadAsset = async (file: File | null) => {
    if (!file) return;
    setUploading(true);
    setNotice("");
    try {
      const publicUrl = await uploadModelAsset(file);
      setAssetUrl(publicUrl);
      setContent((prev) => `${prev}\n\n![asset](${publicUrl})\n`);
      setNotice("asset uploaded and url inserted");
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <section className="klyxe-panel p-4">
        <h2 className="mb-3 text-lg font-semibold">author editor</h2>
        <label className="mb-3 block">
          <span className="mb-1 block text-xs uppercase text-zinc-400">title</span>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded border border-zinc-800 bg-black px-3 py-2 text-sm"
            placeholder="article title"
          />
        </label>
        <label className="mb-3 block">
          <span className="mb-1 block text-xs uppercase text-zinc-400">content mdx</span>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="h-72 w-full rounded border border-zinc-800 bg-black px-3 py-2 font-mono text-xs"
            placeholder="# write your mdx"
          />
        </label>
        <div className="mb-3 flex flex-wrap gap-2">
          <button className="rounded border border-zinc-700 px-3 py-1 text-sm" onClick={saveDraft}>
            save draft
          </button>
          <button className="rounded border border-[#39ff14]/40 px-3 py-1 text-sm text-[#39ff14]" onClick={publish}>
            publish
          </button>
          <span className="self-center text-xs text-zinc-500">status: {status}</span>
        </div>
        <label className="block">
          <span className="mb-1 block text-xs uppercase text-zinc-400">asset upload</span>
          <input type="file" onChange={(e) => void uploadAsset(e.target.files?.[0] || null)} disabled={uploading} />
        </label>
        {assetUrl ? <p className="mt-2 text-xs text-zinc-400">last asset: {assetUrl}</p> : null}
        {notice ? <p className="mt-2 text-xs text-zinc-300">{notice}</p> : null}
      </section>
      <section className="klyxe-panel p-4">
        <h2 className="mb-3 text-lg font-semibold">preview</h2>
        <MdxRenderer source={previewSource} />
      </section>
    </div>
  );
}
