"use client";

import { useApiKeys, type KeyProvider } from "@/components/shared/presets/api-key-context";

const rows: Array<{ provider: KeyProvider; label: string }> = [
  { provider: "openai", label: "OpenAI_Key" },
  { provider: "anthropic", label: "Anthropic_Key" },
  { provider: "gemini", label: "Gemini_Key" }
];

export function ApiKeyManager() {
  const { keys, setKey } = useApiKeys();

  const valueMap: Record<KeyProvider, string> = {
    openai: keys.OpenAI_Key,
    anthropic: keys.Anthropic_Key,
    gemini: keys.Gemini_Key
  };

  return (
    <div className="klyxe-panel p-4">
      <h2 className="mb-3 text-lg font-semibold">api key manager</h2>
      <div className="space-y-3">
        {rows.map((row) => (
          <label key={row.provider} className="block">
            <span className="mb-1 block text-xs tracking-wider text-zinc-400">{row.label}</span>
            <input
              type="password"
              value={valueMap[row.provider]}
              onChange={(e) => setKey(row.provider, e.target.value)}
              className="w-full rounded border border-zinc-800 bg-black px-3 py-2 text-sm"
              placeholder={`paste ${row.provider} key`}
            />
          </label>
        ))}
      </div>
      <p className="mt-3 text-xs text-zinc-500">keys are client-side only in localstorage</p>
    </div>
  );
}
