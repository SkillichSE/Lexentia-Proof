import { promises as fs } from "node:fs";
import path from "node:path";

async function readJson<T>(relativePath: string, fallback: T): Promise<T> {
  try {
    const fullPath = path.join(process.cwd(), "docs", relativePath);
    const raw = await fs.readFile(fullPath, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export async function loadLegacyNews() {
  return readJson<Array<{ title?: string; summary?: string; date?: string }>>("data/results/news.json", []);
}

export async function loadLegacySummary() {
  return readJson<Record<string, unknown>>("data/results/summary.json", {});
}
