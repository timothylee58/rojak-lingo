"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Badge, Card } from "@/components/ui/card";
import { MODEL_ORDER, TASKS, modelStyle } from "@/lib/config";
import type { Leaderboard as Data, ModelSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

type Task = (typeof TASKS)[number];
type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: Data };

function useLeaderboard(): State {
  const [state, setState] = useState<State>({ status: "loading" });
  useEffect(() => {
    const sample = new URLSearchParams(window.location.search).has("sample");
    fetch(sample ? "./leaderboard.sample.json" : "./leaderboard.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<Data>;
      })
      .then((data) => setState({ status: "ready", data }))
      .catch((e: Error) => setState({ status: "error", message: e.message }));
  }, []);
  return state;
}

const pct = (v: number) => (v * 100).toFixed(1);

const shortDate = (iso: string) =>
  new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });

function scoreOf(model: ModelSummary | undefined, task: Task): number | undefined {
  return model?.metrics[task.key]?.[task.metric];
}

function taskDelta(models: Record<string, ModelSummary>, task: Task): number | undefined {
  const base = scoreOf(models["base"], task);
  const ft = scoreOf(models["rojak-ft"], task);
  return base !== undefined && ft !== undefined ? (ft - base) * 100 : undefined;
}

function Bar({
  value,
  color,
  label,
  name,
  index,
}: {
  value: number;
  color: string;
  label: string;
  name: string;
  index: number;
}) {
  const reduce = useReducedMotion();
  const width = `${Math.max(0, Math.min(1, value)) * 100}%`;
  return (
    <div>
      <p className="mb-1 text-xs text-muted">{name}</p>
      <div className="flex items-center gap-3">
        <div className="h-3 flex-1 overflow-hidden rounded-full bg-line" role="img" aria-label={`${label}: ${pct(value)}`}>
          <motion.div
            className={cn("h-full rounded-full", color)}
            initial={{ width: reduce ? width : 0 }}
            animate={{ width }}
            transition={{ duration: 0.7, ease: "easeOut", delay: reduce ? 0 : Math.min(index * 0.08, 0.4) }}
          />
        </div>
        <span className="w-12 text-right font-mono text-sm tabular-nums">{pct(value)}</span>
      </div>
    </div>
  );
}

function Banner({ children, tone }: { children: React.ReactNode; tone: "warn" | "info" }) {
  return (
    <div
      role="status"
      className={cn(
        "mb-4 rounded-lg border px-4 py-3 text-sm",
        tone === "warn"
          ? "border-amber-500/50 bg-amber-500/10 text-fg"
          : "border-line bg-card text-muted",
      )}
    >
      {children}
    </div>
  );
}

function Delta({ task, models }: { task: Task; models: Record<string, ModelSummary> }) {
  const delta = taskDelta(models, task);
  return (
    <Card>
      <p className="text-sm text-muted">{task.title}</p>
      <p
        className={cn(
          "mt-1 font-mono text-3xl font-semibold tabular-nums",
          delta === undefined ? "text-muted" : delta >= 0 ? "text-ft" : "text-fg",
        )}
      >
        {delta === undefined ? "—" : `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}`}
      </p>
      <p className="mt-1 text-xs text-muted">points vs base · {task.metricLabel}</p>
    </Card>
  );
}

function Help() {
  return (
    <>
      Run <code className="font-mono">make eval {"&&"} make report</code> then{" "}
      <code className="font-mono">make web-data</code>, or open this page with{" "}
      <code className="font-mono">?sample</code> to preview the layout.
    </>
  );
}

export function Leaderboard() {
  const state = useLeaderboard();

  if (state.status === "loading") {
    return <p className="text-muted">Loading results…</p>;
  }
  if (state.status === "error") {
    return (
      <Banner tone="info">
        No results found ({state.message}). <Help />
      </Banner>
    );
  }

  const { data } = state;
  const models = data.models;
  const known = MODEL_ORDER.filter((m) => models[m]);
  const extra = Object.keys(models).filter((m) => !MODEL_ORDER.includes(m)).sort();
  const present = [...known, ...extra];
  const drafts = Math.max(0, ...Object.values(models).map((m) => m.n_draft_items));
  const items = present.length > 0 ? (models[present[0] as string]?.n_items ?? "?") : "?";

  if (present.length === 0) {
    return (
      <Banner tone="info">
        No models in these results yet. <Help />
      </Banner>
    );
  }

  const deltas = TASKS.map((t) => taskDelta(models, t));
  // Average the values as displayed (1dp), so the verdict reconciles with the cards.
  const defined = deltas
    .filter((d): d is number => d !== undefined)
    .map((d) => Math.round(d * 10) / 10);
  const avg = defined.length > 0 ? defined.reduce((a, b) => a + b, 0) / defined.length : undefined;

  return (
    <div>
      {data.sample && (
        <Banner tone="warn">
          <strong>Sample data.</strong> These numbers are placeholders to preview the layout, not real results.
        </Banner>
      )}
      {drafts > 0 && !data.sample && (
        <Banner tone="warn">
          {drafts} gold items are still unverified drafts. Verify them before quoting these numbers.
        </Banner>
      )}

      <p className="mb-10 text-sm text-muted">
        {items} gold items · {present.length} {present.length === 1 ? "model" : "models"} · Updated{" "}
        {shortDate(data.generated)}
      </p>

      <section aria-labelledby="delta-h" className="mb-12">
        <h2 id="delta-h" className="mb-1 text-xl font-semibold">
          Does fine-tuning help?
        </h2>
        <p className={cn("mb-4", avg === undefined ? "text-sm text-muted" : "text-lg font-medium text-fg")}>
          {avg === undefined
            ? "Evaluate the base model and the fine-tune to see the comparison."
            : avg >= 0
              ? `The fine-tune gains +${avg.toFixed(1)} points on average${defined.length < TASKS.length ? ` across ${defined.length} of ${TASKS.length} tasks` : ""}.`
              : `The fine-tune trails by ${Math.abs(avg).toFixed(1)} points on average${defined.length < TASKS.length ? ` across ${defined.length} of ${TASKS.length} tasks` : ""}.`}
        </p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {TASKS.map((t) => (
            <Delta key={t.key} task={t} models={models} />
          ))}
        </div>
      </section>

      <section aria-labelledby="tasks-h" className="mb-12">
        <h2 id="tasks-h" className="mb-4 text-xl font-semibold">
          Scores by task
        </h2>
        <div className="mb-4 flex flex-wrap gap-2">
          {present.map((m) => (
            <Badge key={m}>
              <span className={cn("mr-1.5 inline-block h-2 w-2 rounded-full", modelStyle(m).color)} aria-hidden />
              {modelStyle(m).label}
            </Badge>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {TASKS.map((task) => (
            <Card key={task.key}>
              <div className="mb-4 flex items-baseline justify-between gap-2">
                <h3 className="font-semibold">{task.title}</h3>
                <span className="font-mono text-xs text-muted">
                  {task.metricLabel} · n={models[present[0] as string]?.metrics[task.key]?.n ?? "?"}
                </span>
              </div>
              <p className="mb-4 text-sm text-muted">{task.blurb}</p>
              <div className="space-y-3">
                {present.map((m, i) => {
                  const v = scoreOf(models[m], task);
                  return v === undefined ? null : (
                    <Bar
                      key={m}
                      value={v}
                      color={modelStyle(m).color}
                      name={modelStyle(m).label}
                      label={`${modelStyle(m).label} ${task.title}`}
                      index={i}
                    />
                  );
                })}
              </div>
            </Card>
          ))}
        </div>
      </section>

      <section aria-labelledby="table-h">
        <h2 id="table-h" className="mb-4 text-xl font-semibold">
          All numbers
        </h2>
        <div className="overflow-x-auto rounded-xl border border-line bg-card">
          <table className="w-full min-w-[32rem] text-left text-sm">
            <thead className="text-muted">
              <tr className="border-b border-line">
                <th scope="col" className="px-4 py-3 font-medium">Model</th>
                {TASKS.map((t) => (
                  <th key={t.key} scope="col" className="px-4 py-3 text-right font-medium whitespace-nowrap">
                    {t.title} <span className="font-normal">({t.metricLabel})</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {present.map((m) => (
                <tr key={m} className="border-b border-line last:border-0">
                  <th scope="row" className="px-4 py-3">
                    <span className="font-medium">{modelStyle(m).label}</span>
                    <span className="block text-xs font-normal text-muted">
                      {shortDate(models[m]?.created ?? data.generated)} · {models[m]?.n_items ?? "?"} items
                    </span>
                  </th>
                  {TASKS.map((t) => {
                    const v = scoreOf(models[m], t);
                    const rivals = present
                      .map((o) => scoreOf(models[o], t))
                      .filter((x): x is number => x !== undefined);
                    const best = rivals.length > 1 && v !== undefined && v === Math.max(...rivals);
                    const acc = t.key === "intent" ? models[m]?.metrics.intent?.accuracy : undefined;
                    return (
                      <td
                        key={t.key}
                        className={cn("px-4 py-3 text-right font-mono tabular-nums", best && "font-semibold")}
                      >
                        {v === undefined ? <span className="text-muted">—</span> : pct(v)}
                        {acc !== undefined && (
                          <span className="block font-sans text-xs font-normal text-muted">
                            acc {pct(acc)}
                          </span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {present.length > 1 && (
          <p className="mt-2 text-xs text-muted">Bold marks the best score per task.</p>
        )}
      </section>
    </div>
  );
}
