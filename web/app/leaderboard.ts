import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

export type TaskMetrics = Record<string, number>;
export type Summary = {
  model: string;
  created: string;
  n_items: number;
  n_draft_items: number;
  metrics: Record<string, TaskMetrics>;
};
export type Leaderboard = { generated: string; models: Record<string, Summary> };

// Headline metric per task; mirrors the README task table.
export const TASKS: { task: string; metric: string; label: string }[] = [
  { task: "normalize", metric: "chrf", label: "Normalize (chrF)" },
  { task: "intent", metric: "macro_f1", label: "Intent (macro-F1)" },
  { task: "instruct", metric: "pass_rate", label: "Instruct (pass rate)" },
  { task: "translate", metric: "chrf", label: "Translate (chrF)" },
];

// Read at build time so the exported site is fully static.
export function loadLeaderboard(): Leaderboard | null {
  const file = path.join(process.cwd(), "..", "results", "leaderboard.json");
  if (!existsSync(file)) return null;
  return JSON.parse(readFileSync(file, "utf-8"));
}
