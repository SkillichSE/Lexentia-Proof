"use client";

import type { ComponentType } from "react";
import { useApiKeys, type KeyProvider } from "@/components/shared/presets/api-key-context";

type WithKeyRequiredOptions = {
  provider: KeyProvider;
};

export function withKeyRequired<P extends Record<string, unknown>>(
  Component: ComponentType<P>,
  options: WithKeyRequiredOptions
) {
  const Wrapped = (props: P) => {
    const { getKey } = useApiKeys();
    const key = getKey(options.provider);
    if (!key) {
      return (
        <div className="my-6 rounded-xl border border-zinc-800 bg-zinc-950/70 p-4">
          <p className="text-sm text-zinc-300">Для взаимодействия введите ваш API ключ в настройках</p>
          <a href="/dashboard" className="mt-2 inline-block text-sm text-[#39ff14] hover:underline">
            открыть менеджер ключей
          </a>
        </div>
      );
    }
    return <Component {...props} />;
  };
  Wrapped.displayName = `WithKeyRequired(${Component.displayName || Component.name || "Component"})`;
  return Wrapped;
}
