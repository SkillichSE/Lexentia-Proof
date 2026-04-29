"use client";

import { useState } from "react";

export function CodeRunner() {
  const [code, setCode] = useState("return 'hello from sandbox';");
  const [output, setOutput] = useState("");

  const run = () => {
    try {
      // sandboxed function runner without external scope
      const fn = new Function(`"use strict"; ${code}`);
      const result = fn();
      setOutput(String(result ?? ""));
    } catch (err) {
      setOutput(err instanceof Error ? err.message : "execution failed");
    }
  };

  return (
    <div className="my-6 rounded-xl border border-zinc-800 bg-zinc-950/70 p-4">
      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-200">code runner</h3>
      <textarea
        className="h-32 w-full rounded border border-zinc-800 bg-black px-3 py-2 font-mono text-xs"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <div className="mt-2 flex items-center gap-2">
        <button className="rounded border border-zinc-700 px-3 py-1 text-sm hover:border-zinc-500" onClick={run}>
          run js
        </button>
      </div>
      <pre className="mt-3 rounded border border-zinc-800 bg-black p-3 text-xs text-zinc-300">{output || "output"}</pre>
    </div>
  );
}
