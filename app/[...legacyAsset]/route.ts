import { promises as fs } from "node:fs";
import path from "node:path";

const mimeTypes: Record<string, string> = {
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf"
};

function sanitize(parts: string[]) {
  return parts.join("/").replace(/\.\./g, "");
}

export async function GET(_: Request, context: { params: { legacyAsset: string[] } }) {
  const parts = context.params.legacyAsset || [];
  const rawPath = sanitize(parts);
  const ext = path.extname(rawPath).toLowerCase();
  if (!ext || ext === ".html") {
    return new Response("not found", { status: 404 });
  }

  const fullPath = path.join(process.cwd(), "docs", rawPath);
  try {
    const content = await fs.readFile(fullPath);
    return new Response(content, {
      headers: {
        "content-type": mimeTypes[ext] || "application/octet-stream",
        "cache-control": "public, max-age=3600"
      }
    });
  } catch {
    return new Response("not found", { status: 404 });
  }
}
