"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

export type KeyProvider = "openai" | "anthropic" | "gemini";

type ApiKeys = {
  OpenAI_Key: string;
  Anthropic_Key: string;
  Gemini_Key: string;
};

type ApiKeyContextValue = {
  keys: ApiKeys;
  setKey: (provider: KeyProvider, value: string) => void;
  getKey: (provider: KeyProvider) => string | null;
};

const storageKey = "klyxe_byok_v1";

const emptyKeys: ApiKeys = {
  OpenAI_Key: "",
  Anthropic_Key: "",
  Gemini_Key: ""
};

const ApiKeyContext = createContext<ApiKeyContextValue | null>(null);

function toStorageKey(provider: KeyProvider): keyof ApiKeys {
  if (provider === "openai") return "OpenAI_Key";
  if (provider === "anthropic") return "Anthropic_Key";
  return "Gemini_Key";
}

export function ApiKeyProvider({ children }: { children: ReactNode }) {
  const [keys, setKeys] = useState<ApiKeys>(emptyKeys);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return;
      const parsed = JSON.parse(raw) as Partial<ApiKeys>;
      setKeys({
        OpenAI_Key: parsed.OpenAI_Key || "",
        Anthropic_Key: parsed.Anthropic_Key || "",
        Gemini_Key: parsed.Gemini_Key || ""
      });
    } catch {
      setKeys(emptyKeys);
    }
  }, []);

  const value = useMemo<ApiKeyContextValue>(
    () => ({
      keys,
      setKey(provider, keyValue) {
        const field = toStorageKey(provider);
        const next = { ...keys, [field]: keyValue };
        setKeys(next);
        localStorage.setItem(storageKey, JSON.stringify(next));
      },
      getKey(provider) {
        const field = toStorageKey(provider);
        const value = keys[field]?.trim();
        return value ? value : null;
      }
    }),
    [keys]
  );

  return <ApiKeyContext.Provider value={value}>{children}</ApiKeyContext.Provider>;
}

export function useApiKeys() {
  const context = useContext(ApiKeyContext);
  if (!context) throw new Error("useApiKeys must be used inside ApiKeyProvider");
  return context;
}
