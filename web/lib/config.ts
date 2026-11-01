import type { TaskKey, TaskMetrics } from "./types";

export const TASKS: {
  key: TaskKey;
  title: string;
  blurb: string;
  metric: keyof TaskMetrics;
  metricLabel: string;
}[] = [
  { key: "normalize", title: "Normalize", blurb: "Rojak message to standard English", metric: "chrf", metricLabel: "chrF" },
  { key: "intent", title: "Intent", blurb: "Classify a code-switched customer message", metric: "macro_f1", metricLabel: "Macro-F1" },
  { key: "instruct", title: "Instruct", blurb: "Follow mixed-language instructions with checkable constraints", metric: "pass_rate", metricLabel: "Pass rate" },
  { key: "translate", title: "Translate", blurb: "Translate between English, BM and Mandarin", metric: "chrf", metricLabel: "chrF" },
];

// Fixed order so the base-vs-fine-tune comparison always reads the same way.
export const MODELS: Record<string, { label: string; color: string }> = {
  base: { label: "Base model", color: "bg-base" },
  "rojak-ft": { label: "Rojak-Lingo fine-tune", color: "bg-ft" },
  "muse-spark": { label: "Muse Spark (reference)", color: "bg-ref" },
};

export const MODEL_ORDER = Object.keys(MODELS);

// Unknown keys (e.g. a mock "oracle" run) get a neutral style instead of crashing.
export function modelStyle(key: string): { label: string; color: string } {
  return MODELS[key] ?? { label: key, color: "bg-muted" };
}
