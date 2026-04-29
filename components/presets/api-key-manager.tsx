"use client";

import { useEffect, useState } from "react";

type Provider = "openai" | "anthropic" | "gemini";

const storageKey = "klyxe_byok_v1";
const providers: Provider[] = ["openai", "anthropic", "gemini"];

export function getStoredKey(provider: Provider): string {
  if (typeof window === "undefined") return "";
  try {
    const parsed = JSON.parse(localStorage.getItem(storageKey) || "{}");
    return parsed[provider] || "";
  } catch {
    return "";
  }
}

export function ApiKeyManager() {
  const [keys, setKeys] = useState<Record<Provider, string>>({
    openai: "",
    anthropic: "",
    gemini: ""
  });

  useEffect(() => {
    setKeys({
      openai: getStoredKey("openai"),
      anthropic: getStoredKey("anthropic"),
      gemini: getStoredKey("gemini")
    });
  }, []);

  const onChange = (provider: Provider, value: string) => {
    const next = { ...keys, [provider]: value };
    setKeys(next);
    localStorage.setItem(storageKey, JSON.stringify(next));
  };

  return (
    <div className="klyxe-panel p-4">
      <h2 className="mb-3 text-lg font-semibold">api key manager</h2>
      <div className="space-y-3">
        {providers.map((provider) => (
          <label key={provider} className="block">
            <span className="mb-1 block text-xs uppercase tracking-wider text-zinc-400">{provider}</span>
            <input
              type="password"
              value={keys[provider]}
              onChange={(e) => onChange(provider, e.target.value)}
              placeholder={`paste ${provider} key`}
              className="w-full rounded border border-zinc-800 bg-black px-3 py-2 text-sm"
            />
          </label>
        ))}
      </div>
      <p className="mt-3 text-xs text-zinc-500">keys stay in localstorage only and never reach klyxe server</p>
    </div>
  );
}
