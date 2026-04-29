import { promises as fs } from "node:fs";
import path from "node:path";

const contentTypeByExt: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp"
};

function safePath(parts: string[]) {
  const normalized = parts.join("/").replace(/\.\./g, "");
  return path.join(process.cwd(), "docs", normalized);
}

export async function GET(_: Request, context: { params: { path: string[] } }) {
  const parts = context.params.path || [];
  const primary = safePath(parts);
  const candidates = [primary, `${primary}.html`, path.join(primary, "index.html")];

  for (const filePath of candidates) {
    try {
      const buffer = await fs.readFile(filePath);
      const ext = path.extname(filePath).toLowerCase();
      const type = contentTypeByExt[ext] || "text/plain; charset=utf-8";
      return new Response(buffer, { headers: { "content-type": type } });
    } catch {
      continue;
    }
  }
  return new Response("not found", { status: 404 });
}
