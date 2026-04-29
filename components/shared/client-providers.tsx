"use client";

import type { ReactNode } from "react";
import { ApiKeyProvider } from "@/components/shared/presets/api-key-context";

export function ClientProviders({ children }: { children: ReactNode }) {
  return <ApiKeyProvider>{children}</ApiKeyProvider>;
}
