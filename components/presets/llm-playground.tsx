"use client";

import { useState } from "react";
import { AIDemoShell } from "@/components/presets/ai-demo-shell";
import { useApiKeys } from "@/components/shared/presets/api-key-context";
import { withKeyRequired } from "@/components/shared/presets/with-key-required";

type LLMPlaygroundProps = {
  provider?: "openai" | "anthropic" | "gemini";
  model?: string;
};

function LLMPlaygroundBase({ provider = "openai", model = "gpt-4o-mini" }: LLMPlaygroundProps) {
  const { getKey } = useApiKeys();
  const [prompt, setPrompt] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const endpointMap = {
    openai: "https://api.openai.com/v1/chat/completions",
    anthropic: "https://api.anthropic.com/v1/messages",
    gemini: "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
  } as const;

  const run = async () => {
    const key = getKey(provider);
    if (!key) {
      setError("missing key");
      return;
    }
    setLoading(true);
    setError(null);
    setReply("");
    try {
      if (provider === "anthropic") {
        const response = await fetch(endpointMap.anthropic, {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01"
          },
          body: JSON.stringify({
            model: "claude-3-5-haiku-latest",
            max_tokens: 512,
            messages: [{ role: "user", content: prompt }]
          })
        });
        if (!response.ok) throw new Error(`request failed ${response.status}`);
        const data = (await response.json()) as { content?: Array<{ text?: string }> };
        setReply(data.content?.[0]?.text || "");
      } else if (provider === "gemini") {
        const response = await fetch(`${endpointMap.gemini}?key=${encodeURIComponent(key)}`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }]
          })
        });
        if (!response.ok) throw new Error(`request failed ${response.status}`);
        const data = (await response.json()) as {
          candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
        };
        setReply(data.candidates?.[0]?.content?.parts?.[0]?.text || "");
      } else {
        const response = await fetch(endpointMap.openai, {
          method: "POST",
          headers: {
            "content-type": "application/json",
            authorization: `Bearer ${key}`
          },
          body: JSON.stringify({
            model,
            messages: [{ role: "user", content: prompt }]
          })
        });
        if (!response.ok) throw new Error(`request failed ${response.status}`);
        const data = (await response.json()) as {
          choices?: Array<{ message?: { content?: string } }>;
        };
        setReply(data.choices?.[0]?.message?.content || "");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AIDemoShell title={`llm playground (${provider})`} loading={loading} progress={loading ? 65 : 100} error={error}>
      <div className="space-y-2">
        <textarea
          className="h-24 w-full rounded border border-zinc-800 bg-black px-3 py-2 text-sm"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="ask the model"
        />
        <button
          className="rounded border border-[#39ff14]/40 px-3 py-1 text-sm text-[#39ff14] disabled:opacity-50"
          onClick={run}
          disabled={loading || !prompt.trim()}
        >
          run
        </button>
        {reply ? <pre className="rounded border border-zinc-800 bg-black p-3 text-sm text-zinc-200">{reply}</pre> : null}
      </div>
    </AIDemoShell>
  );
}

const WrappedOpenAI = withKeyRequired(LLMPlaygroundBase, { provider: "openai" });
const WrappedAnthropic = withKeyRequired(LLMPlaygroundBase, { provider: "anthropic" });
const WrappedGemini = withKeyRequired(LLMPlaygroundBase, { provider: "gemini" });

export function LLMPlayground({ provider = "openai", model = "gpt-4o-mini" }: LLMPlaygroundProps) {
  if (provider === "anthropic") return <WrappedAnthropic provider={provider} model={model} />;
  if (provider === "gemini") return <WrappedGemini provider={provider} model={model} />;
  return <WrappedOpenAI provider={provider} model={model} />;
}
