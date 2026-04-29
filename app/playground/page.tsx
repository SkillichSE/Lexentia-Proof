import { LLMPlayground } from "@/components/presets/llm-playground";
import { ApiKeyManager } from "@/components/shared/presets/api-key-manager";

export default function PlaygroundPage() {
  return (
    <div className="klyxe-container py-10">
      <h1 className="mb-6 text-2xl font-bold">llm playground</h1>
      <div className="grid gap-4 lg:grid-cols-2">
        <ApiKeyManager />
        <LLMPlayground provider="openai" />
      </div>
    </div>
  );
}
