"use client";

import { useEffect, useRef, useState } from "react";
import { AIDemoShell } from "@/components/presets/ai-demo-shell";
import { useLazyVisibility } from "@/lib/ai/use-lazy-visibility";

type CanvasPreviewProps = {
  modelUrl?: string;
};

export function CanvasPreview({ modelUrl }: CanvasPreviewProps) {
  const { ref, visible } = useLazyVisibility<HTMLDivElement>();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const modelRef = useRef<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<string>("-");

  useEffect(() => {
    let active = true;
    if (!visible) return;
    const load = async () => {
      setLoading(true);
      setError(null);
      setProgress(10);
      try {
        const tf = await import("@tensorflow/tfjs");
        if (!active) return;
        setProgress(45);
        if (modelUrl) {
          modelRef.current = await tf.loadLayersModel(modelUrl);
          if (!active) return;
          setProgress(100);
        } else {
          setProgress(100);
        }
        const canvas = canvasRef.current;
        if (canvas) {
          const ctx = canvas.getContext("2d");
          if (ctx) {
            ctx.fillStyle = "black";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
          }
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : "failed to load canvas runtime";
        setError(message);
      } finally {
        if (!active) return;
        setLoading(false);
      }
    };
    void load();
    return () => {
      active = false;
    };
  }, [visible, modelUrl]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";

    let drawing = false;
    const draw = (x: number, y: number) => {
      ctx.lineTo(x, y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x, y);
    };

    const pointerDown = (e: PointerEvent) => {
      drawing = true;
      const rect = canvas.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * canvas.width;
      const y = ((e.clientY - rect.top) / rect.height) * canvas.height;
      ctx.beginPath();
      ctx.moveTo(x, y);
    };
    const pointerMove = (e: PointerEvent) => {
      if (!drawing) return;
      const rect = canvas.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * canvas.width;
      const y = ((e.clientY - rect.top) / rect.height) * canvas.height;
      draw(x, y);
    };
    const stop = () => {
      drawing = false;
      ctx.beginPath();
    };

    canvas.addEventListener("pointerdown", pointerDown);
    canvas.addEventListener("pointermove", pointerMove);
    canvas.addEventListener("pointerup", stop);
    canvas.addEventListener("pointerleave", stop);
    return () => {
      canvas.removeEventListener("pointerdown", pointerDown);
      canvas.removeEventListener("pointermove", pointerMove);
      canvas.removeEventListener("pointerup", stop);
      canvas.removeEventListener("pointerleave", stop);
    };
  }, []);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setPrediction("-");
  };

  const predict = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    try {
      const tf = await import("@tensorflow/tfjs");
      const image = tf.browser.fromPixels(canvas, 1).toFloat().div(255).reshape([1, 28, 28, 1]);
      const model = modelRef.current as { predict?: (input: unknown) => unknown } | null;
      if (model?.predict) {
        const output = model.predict(image) as { data?: () => Promise<Float32Array> };
        const data = output?.data ? await output.data() : new Float32Array();
        const best = data.reduce(
          (acc, value, idx) => (value > acc.value ? { value, idx } : acc),
          { value: -Infinity, idx: 0 }
        );
        setPrediction(String(best.idx));
      } else {
        const avg = (await image.mean().data())[0];
        setPrediction(avg > 0.15 ? "ink detected" : "empty");
      }
      tf.dispose(image);
    } catch (err) {
      setError(err instanceof Error ? err.message : "predict failed");
    }
  };

  return (
    <div ref={ref}>
      <AIDemoShell title="canvas preview" loading={loading} progress={progress} error={error}>
        <div className="rounded border border-zinc-800 bg-black p-4">
          <p className="mb-2 text-xs text-zinc-400">model: {modelUrl || "local default model"}</p>
          <canvas
            ref={canvasRef}
            width={28}
            height={28}
            className="h-56 w-56 touch-none rounded border border-zinc-700 bg-zinc-900 [image-rendering:pixelated]"
          />
          <div className="mt-3 flex items-center gap-2">
            <button className="rounded border border-zinc-700 px-3 py-1 text-xs" onClick={predict}>
              predict
            </button>
            <button className="rounded border border-zinc-700 px-3 py-1 text-xs" onClick={clearCanvas}>
              clear
            </button>
            <span className="text-xs text-zinc-400">result: {prediction}</span>
          </div>
        </div>
      </AIDemoShell>
    </div>
  );
}
