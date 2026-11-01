export type TaskKey = "normalize" | "intent" | "instruct" | "translate";

export interface TaskMetrics {
  n: number;
  chrf?: number;
  accuracy?: number;
  macro_f1?: number;
  pass_rate?: number;
}

export interface ModelSummary {
  model: string;
  created: string;
  n_items: number;
  n_draft_items: number;
  metrics: Partial<Record<TaskKey, TaskMetrics>>;
}

export interface Leaderboard {
  generated: string;
  sample?: boolean;
  models: Record<string, ModelSummary>;
}
